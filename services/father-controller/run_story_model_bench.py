import json
import time
import urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parent
CONFIG=json.loads((BASE/"config/story_model_config.json").read_text(encoding="utf-8"))
TASKS=json.loads((BASE/"config/story_benchmark_tasks.json").read_text(encoding="utf-8"))
OLLAMA="http://127.0.0.1:11434"

SYSTEM="""Ты профессиональный литературный соавтор. Сохраняй стиль, характеры, атмосферу и причинно-следственные связи. Выполняй редакторские уточнения точно. Возвращай только художественный текст."""

def get_json(url):
    with urllib.request.urlopen(url,timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def post_json(url,payload,timeout=180):
    raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(url,data=raw,headers={"Content-Type":"application/json; charset=utf-8"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

installed={m.get("name","") for m in get_json(OLLAMA+"/api/tags").get("models",[])}

def present(model):
    return model in installed or any(x.startswith(model+":") for x in installed)

results=[]
for candidate in CONFIG["candidates"]:
    model=candidate["runtime_model"]
    if not present(model):
        results.append({"model":model,"status":"MISSING"})
        print("SKIP",model,"not installed",flush=True)
        continue

    print("\n===",model,"===",flush=True)
    item={"model":model,"candidate_id":candidate["id"],"status":"OK","tasks":[]}

    for task in TASKS["tasks"]:
        print("START",task["id"],"mode="+task["mode"],"model="+model,flush=True)

        prompt=f"""РЕЖИМ: {task['mode']}
УТОЧНЕНИЕ: {task['prompt']}

ИСХОДНЫЙ ТЕКСТ:
{task['text']}"""

        t0=time.perf_counter()
        try:
            data=post_json(OLLAMA+"/api/chat",{
                "model":model,
                "messages":[
                    {"role":"system","content":SYSTEM},
                    {"role":"user","content":prompt}
                ],
                "stream":False,
                "options":{
                    "temperature":0.9,
                    "top_p":0.95,
                    "num_predict":1200
                }
            })

            elapsed=round((time.perf_counter()-t0)*1000,2)
            out=data.get("message",{}).get("content","")

            row={
                "task_id":task["id"],
                "mode":task["mode"],
                "latency_ms":elapsed,
                "chars":len(out),
                "output":out
            }
            item["tasks"].append(row)
            print("DONE",task["id"],elapsed,"ms",len(out),"chars",flush=True)

        except Exception as e:
            elapsed=round((time.perf_counter()-t0)*1000,2)
            err=type(e).__name__+": "+str(e)
            item["tasks"].append({
                "task_id":task["id"],
                "latency_ms":elapsed,
                "error":err
            })
            item["status"]="PARTIAL"
            print("FAIL",task["id"],elapsed,"ms",err,flush=True)

    good=[x for x in item["tasks"] if "output" in x]
    item["summary"]={
        "completed":len(good),
        "avg_latency_ms":round(sum(x["latency_ms"] for x in good)/len(good),2) if good else None,
        "avg_chars":round(sum(x["chars"] for x in good)/len(good),1) if good else None
    }
    results.append(item)

report={
    "benchmark":"FATHER STORY MODEL BENCH v1.1",
    "principle":"same prompts; no automatic semantic winner; human selects champion after side-by-side review",
    "dimensions":TASKS["dimensions"],
    "results":results
}

out=BASE/"evidence/story_model_bench_latest.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nREPORT:",out,flush=True)
print("NOTE: quality winner must be selected after reading outputs; latency alone does not choose champion.",flush=True)
