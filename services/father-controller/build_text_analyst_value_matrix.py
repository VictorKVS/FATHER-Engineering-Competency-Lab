import json, re
from pathlib import Path

BASE=Path(__file__).resolve().parent
Q=BASE/"evidence/text_analyst_quality/quality_latest.json"
E=BASE/"evidence/resource_energy"
W=BASE/"evidence/text_analyst_value"
OUT=W/"value_matrix_latest.json"
QUALITY_GATE=50.0
THERMAL_GATE_C=90.0

MODELS=[
 "qwen2.5:3b",
 "qwen2.5:7b",
 "qwen2.5-coder:7b-instruct-q4_K_M",
 "llama3.2:1b"
]

def safe(s): return re.sub(r"[^A-Za-z0-9_.-]+","_",s)

quality=json.loads(Q.read_text(encoding="utf-8"))
qmap={m["model"]:m.get("summary",{}) for m in quality.get("models",[])}

rows=[]
for model in MODELS:
    wf=W/f"value_workload_{safe(model)}.json"
    if not wf.exists():
        rows.append({"model":model,"status":"MISSING_WORKLOAD"}); continue
    wd=json.loads(wf.read_text(encoding="utf-8"))

    candidates=[]
    for p in E.glob(f"resource_energy_*_{safe(model)}.json"):
        try:
            d=json.loads(p.read_text(encoding="utf-8"))
            if d.get("label")==model: candidates.append((p.stat().st_mtime,p,d))
        except Exception: pass
    if not candidates:
        rows.append({"model":model,"status":"MISSING_ENERGY"}); continue
    _,ep,ed=max(candidates,key=lambda x:x[0])

    qs=qmap.get(model,{})
    rows.append({
      "model":model,
      "status":"OK",
      "quality_score":qs.get("quality_score"),
      "semantic_judge_avg":qs.get("semantic_judge_avg"),
      "avg_latency_ms":wd.get("avg_latency_ms"),
      "completion_rate":wd.get("completion_rate"),
      "energy_wh_total":ed.get("system_estimate",{}).get("energy_wh"),
      "energy_wh_per_task":ed.get("task_estimate",{}).get("energy_wh_per_task"),
      "cost_total":ed.get("system_estimate",{}).get("cost"),
      "cost_per_task":ed.get("task_estimate",{}).get("cost_per_task"),
      "gpu_temp_max_c":ed.get("gpu",{}).get("temp_max_c"),
      "gpu_power_avg_w":ed.get("gpu",{}).get("power_avg_w"),
      "evidence_energy":str(ep)
    })

eligible=[]
for r in rows:
    if r.get("status")!="OK" or r.get("quality_score") is None:
        continue
    if r["quality_score"] < QUALITY_GATE:
        r["admission"]="DISQUALIFIED_QUALITY"
        r["gate_reason"]=f"quality {r['quality_score']} < {QUALITY_GATE}"
        continue
    if r.get("gpu_temp_max_c") is not None and r["gpu_temp_max_c"] >= THERMAL_GATE_C:
        r["admission"]="THERMAL_REVIEW_REQUIRED"
        r["gate_reason"]=f"gpu temp {r['gpu_temp_max_c']}C >= {THERMAL_GATE_C}C project safety gate"
    else:
        r["admission"]="VALUE_ELIGIBLE"
    eligible.append(r)

valid=[r for r in eligible if r.get("admission")=="VALUE_ELIGIBLE"]
if valid:
    lats=[r["avg_latency_ms"] for r in valid if r["avg_latency_ms"] is not None]
    ens=[r["energy_wh_per_task"] for r in valid if r["energy_wh_per_task"] is not None]
    lo,hi=min(lats),max(lats)
    elo,ehi=min(ens),max(ens)
    for r in valid:
        r["speed_score"]=100.0 if hi==lo else round(100*(hi-r["avg_latency_ms"])/(hi-lo),2)
        r["economy_score"]=100.0 if ehi==elo else round(100*(ehi-r["energy_wh_per_task"])/(ehi-elo),2)
        r["value_score"]=round(0.60*r["quality_score"]+0.20*r["speed_score"]+0.20*r["economy_score"],2)
    valid.sort(key=lambda r:-r["value_score"])

report={
  "benchmark":"FATHER TEXT ANALYST VALUE MATRIX MVP-01",
  "policy":{
    "reliability":"gate before value phase",
    "quality_gate":QUALITY_GATE,
    "thermal_gate_c":THERMAL_GATE_C,
    "formula":"0.60*QUALITY + 0.20*SPEED + 0.20*ECONOMY after gates",
    "economy_basis":"estimated system Wh/task; GPU watts/temp measured by nvidia-smi"
  },
  "rows":rows,
  "ranking":[r["model"] for r in valid]
}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

print("=== FATHER VALUE MATRIX ===")
for r in rows:
    if r.get("admission") and r.get("admission")!="VALUE_ELIGIBLE":
        print("GATE",r["model"],r["admission"],r.get("gate_reason"))
for i,r in enumerate(valid,1):
    print(f"{i}. {r['model']} | Q={r['quality_score']} | SPEED={r['speed_score']} | ECON={r['economy_score']} | VALUE={r['value_score']} | Wh/task={r['energy_wh_per_task']}")
print("REPORT:",OUT)
print("RESULT: COMPLETE" if len(valid)==len(MODELS) else "RESULT: PARTIAL")
