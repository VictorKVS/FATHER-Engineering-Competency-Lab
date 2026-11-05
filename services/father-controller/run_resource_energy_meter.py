import argparse, csv, json, os, subprocess, sys, threading, time
from datetime import datetime, timezone
from pathlib import Path

BASE=Path(__file__).resolve().parent
OUT=BASE/"evidence/resource_energy"
OUT.mkdir(parents=True,exist_ok=True)

try:
    import psutil
except Exception:
    psutil=None

def nvidia_sample():
    cmd=[
      "nvidia-smi",
      "--query-gpu=timestamp,name,temperature.gpu,power.draw,utilization.gpu,memory.used,memory.total",
      "--format=csv,noheader,nounits"
    ]
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=5,check=True)
        line=p.stdout.strip().splitlines()[0]
        parts=[x.strip() for x in line.split(",")]
        return {
          "gpu_name":parts[1],
          "gpu_temp_c":float(parts[2]),
          "gpu_power_w":float(parts[3]),
          "gpu_util_pct":float(parts[4]),
          "vram_used_mb":float(parts[5]),
          "vram_total_mb":float(parts[6]),
          "gpu_sensor":"nvidia-smi"
        }
    except Exception as e:
        return {"gpu_sensor_error":type(e).__name__+": "+str(e)}

def cpu_sample(cpu_idle_w,cpu_max_w):
    if psutil is None:
        return {"cpu_util_pct":None,"cpu_power_est_w":None,"cpu_sensor":"unavailable"}
    util=float(psutil.cpu_percent(interval=None))
    est=cpu_idle_w+(cpu_max_w-cpu_idle_w)*(util/100.0)
    return {"cpu_util_pct":round(util,1),"cpu_power_est_w":round(est,2),"cpu_sensor":"psutil_estimate"}

def sample_once(cpu_idle_w,cpu_max_w,base_w):
    x={"ts":datetime.now(timezone.utc).isoformat()}
    x.update(nvidia_sample())
    x.update(cpu_sample(cpu_idle_w,cpu_max_w))
    gpu=x.get("gpu_power_w")
    cpu=x.get("cpu_power_est_w")
    if gpu is not None:
        x["system_power_est_w"]=round(gpu+(cpu or 0.0)+base_w,2)
    else:
        x["system_power_est_w"]=None
    return x

def run_meter(args):
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path=OUT/f"resource_energy_{stamp}.csv"
    json_path=OUT/f"resource_energy_{stamp}.json"

    rows=[]
    stop=threading.Event()
    lock=threading.Lock()
    start=time.perf_counter()

    def sampler():
        while not stop.is_set():
            row=sample_once(args.cpu_idle_w,args.cpu_max_w,args.base_w)
            row["elapsed_s"]=round(time.perf_counter()-start,3)
            with lock:
                rows.append(row)
            temp=row.get("gpu_temp_c")
            pw=row.get("system_power_est_w")
            util=row.get("gpu_util_pct")
            vram=row.get("vram_used_mb")
            bits=[]
            if temp is not None: bits.append(f"GPU {temp:.0f}C")
            if util is not None: bits.append(f"{util:.0f}%")
            if vram is not None: bits.append(f"VRAM {vram/1024:.1f}GB")
            if pw is not None: bits.append(f"~{pw:.0f}W system")
            if bits: print("[ENERGY] "+" | ".join(bits),flush=True)
            stop.wait(args.interval)

    t=threading.Thread(target=sampler,daemon=True)
    t.start()

    rc=0
    if args.command:
        print("COMMAND:"," ".join(args.command),flush=True)
        try:
            p=subprocess.run(args.command)
            rc=p.returncode
        finally:
            stop.set()
            t.join(timeout=max(2,args.interval+1))
    else:
        print("Meter running without child command. Press Ctrl+C to stop.",flush=True)
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            stop.set(); t.join(timeout=max(2,args.interval+1))

    duration_s=time.perf_counter()-start
    with lock: data=list(rows)

    fields=[]
    for r in data:
        for k in r:
            if k not in fields: fields.append(k)
    with csv_path.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader(); w.writerows(data)

    # Left-rectangle integration is enough for a 1-2 s telemetry interval.
    gpu_wh=0.0
    sys_wh=0.0
    for i in range(1,len(data)):
        dt=max(0.0,float(data[i]["elapsed_s"])-float(data[i-1]["elapsed_s"]))
        gp=data[i-1].get("gpu_power_w")
        sp=data[i-1].get("system_power_est_w")
        if gp is not None: gpu_wh += float(gp)*dt/3600.0
        if sp is not None: sys_wh += float(sp)*dt/3600.0

    temps=[r["gpu_temp_c"] for r in data if r.get("gpu_temp_c") is not None]
    gpowers=[r["gpu_power_w"] for r in data if r.get("gpu_power_w") is not None]
    spowers=[r["system_power_est_w"] for r in data if r.get("system_power_est_w") is not None]

    summary={
      "meter":"FATHER RESOURCE & ENERGY METER v1",
      "started_at":data[0]["ts"] if data else None,
      "duration_s":round(duration_s,2),
      "samples":len(data),
      "command":args.command,
      "return_code":rc,
      "measurement":{
        "gpu_power":"MEASURED_BY_NVIDIA_SMI",
        "gpu_temperature":"MEASURED_BY_NVIDIA_SMI",
        "cpu_power":"ESTIMATED_FROM_CPU_UTILIZATION" if psutil else "UNAVAILABLE",
        "system_power":"ESTIMATE_GPU_MEASURED_PLUS_CPU_ESTIMATE_PLUS_BASE"
      },
      "assumptions":{
        "cpu_idle_w":args.cpu_idle_w,
        "cpu_max_w":args.cpu_max_w,
        "base_system_w":args.base_w,
        "price_per_kwh":args.price_per_kwh,
        "currency":args.currency
      },
      "gpu":{
        "temp_max_c":max(temps) if temps else None,
        "temp_avg_c":round(sum(temps)/len(temps),2) if temps else None,
        "power_avg_w":round(sum(gpowers)/len(gpowers),2) if gpowers else None,
        "power_max_w":max(gpowers) if gpowers else None,
        "energy_wh_measured":round(gpu_wh,4)
      },
      "system_estimate":{
        "power_avg_w":round(sum(spowers)/len(spowers),2) if spowers else None,
        "power_max_w":max(spowers) if spowers else None,
        "energy_wh":round(sys_wh,4),
        "energy_kwh":round(sys_wh/1000.0,6),
        "cost":round((sys_wh/1000.0)*args.price_per_kwh,4) if args.price_per_kwh>0 else None
      },
      "task_estimate":{
        "task_count":args.task_count if args.task_count>0 else None,
        "energy_wh_per_task":round(sys_wh/args.task_count,4) if args.task_count>0 else None,
        "cost_per_task":round(((sys_wh/1000.0)*args.price_per_kwh)/args.task_count,6)
                         if args.task_count>0 and args.price_per_kwh>0 else None
      },
      "thermal":{
        "warning_threshold_c":args.warn_temp_c,
        "warning":bool(temps and max(temps)>=args.warn_temp_c)
      },
      "artifacts":{"csv":str(csv_path),"json":str(json_path)}
    }
    json_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")

    print("\n=== FATHER RESOURCE & ENERGY SUMMARY ===",flush=True)
    print("DURATION:",round(duration_s/60,2),"min",flush=True)
    print("GPU TEMP max/avg:",summary["gpu"]["temp_max_c"],"/",summary["gpu"]["temp_avg_c"],"C",flush=True)
    print("GPU POWER avg/max:",summary["gpu"]["power_avg_w"],"/",summary["gpu"]["power_max_w"],"W",flush=True)
    print("GPU ENERGY:",summary["gpu"]["energy_wh_measured"],"Wh measured",flush=True)
    print("SYSTEM ENERGY:",summary["system_estimate"]["energy_wh"],"Wh estimated",flush=True)
    if summary["system_estimate"]["cost"] is not None:
        print("ESTIMATED COST:",summary["system_estimate"]["cost"],args.currency,flush=True)
    if summary["task_estimate"]["cost_per_task"] is not None:
        print("ESTIMATED COST/TASK:",summary["task_estimate"]["cost_per_task"],args.currency,flush=True)
    if summary["thermal"]["warning"]:
        print("THERMAL WARNING: GPU reached configured threshold",args.warn_temp_c,"C",flush=True)
    print("CSV:",csv_path,flush=True)
    print("JSON:",json_path,flush=True)
    return rc

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--interval",type=float,default=2.0)
    ap.add_argument("--price-per-kwh",type=float,default=float(os.getenv("FATHER_PRICE_PER_KWH","0") or 0))
    ap.add_argument("--currency",default=os.getenv("FATHER_ENERGY_CURRENCY","RUB"))
    ap.add_argument("--task-count",type=int,default=0)
    ap.add_argument("--cpu-idle-w",type=float,default=10.0)
    ap.add_argument("--cpu-max-w",type=float,default=65.0)
    ap.add_argument("--base-w",type=float,default=40.0,help="motherboard/RAM/storage/fans estimate excluding CPU/GPU")
    ap.add_argument("--warn-temp-c",type=float,default=83.0)
    ap.add_argument("command",nargs=argparse.REMAINDER)
    args=ap.parse_args()
    if args.command and args.command[0]=="--": args.command=args.command[1:]
    raise SystemExit(run_meter(args))

if __name__=="__main__":
    main()
