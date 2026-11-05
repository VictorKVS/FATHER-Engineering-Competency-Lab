import json
from pathlib import Path

from father.core.hybrid_runtime_router import HybridRuntimeRouter

BASE=Path(__file__).resolve().parent
SPEC={
  "product_id":"father-runtime-exec-mvp04",
  "agent_manifest":"config/agents/father_general.json",
  "brain_id":"qwen-analysis",
  "competency_id":"generic",
  "inputs":["api","file"],
  "outputs":["json","file"],
  "knowledge":{"adapter":"folder"},
  "retrieval":{"top_k":5},
  "tools":"default",
  "context_bus":True
}

def add(rows,name,passed,details):
    rows.append({"name":name,"passed":bool(passed),"details":details})
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return bool(passed)

def execute_case(router, task, expected_brain, gpu_temp_c=70):
    built=router.build(task,SPEC,gpu_temp_c=gpu_temp_c)
    if not built.get("ok"):
        return {"ok":False,"stage":"build","details":built}
    product=built["product"]
    event=product["inputs"]["api"].normalize({
      "type":"message",
      "content":task.get("text",""),
      "metadata":{"mvp":"runtime-execution-04"}
    })
    result=product["runtime"].run(event)
    return {
      "ok":result.get("ok"),
      "selected_brain":built["plan"].get("brain_id"),
      "response_brain":result.get("brain_id"),
      "expected_brain":expected_brain,
      "content_chars":len(result.get("content") or ""),
      "error":result.get("error"),
      "fallback_used":built["plan"].get("fallback_used"),
      "source":built["plan"].get("source")
    }

def main():
    r=HybridRuntimeRouter(BASE)
    rows=[]; ok=True

    x=execute_case(r,{"role":"text_analyst","complexity":2,"text":"Кратко объясни принцип FATHER: агент не равен модели."},"qwen-analysis-fast")
    ok &= add(rows,"runtime_executes_qwen3b_selected_brain",
              x.get("ok") and x.get("selected_brain")=="qwen-analysis-fast" and x.get("response_brain")=="qwen-analysis-fast" and x.get("content_chars",0)>0,x)

    x=execute_case(r,{"role":"text_analyst","complexity":4,"text":"Объясни, почему в FATHER сложный анализ должен эскалироваться на более сильную модель."},"qwen-analysis")
    ok &= add(rows,"runtime_executes_qwen7b_escalation",
              x.get("ok") and x.get("selected_brain")=="qwen-analysis" and x.get("response_brain")=="qwen-analysis" and x.get("content_chars",0)>0,x)

    x=execute_case(r,{"role":"edge_fast","complexity":1,"text":"Коротко перефразируй: модель является заменяемым мозгом агента."},"llama-small")
    ok &= add(rows,"runtime_executes_llama_edge",
              x.get("ok") and x.get("selected_brain")=="llama-small" and x.get("response_brain")=="llama-small" and x.get("content_chars",0)>0,x)

    p=r.plan({"role":"text_analyst","complexity":2,"text":"анализ"},SPEC,gpu_temp_c=91)
    ok &= add(rows,"runtime_execution_respects_thermal_block",
              (not p.get("ok")) and p.get("reason")=="thermal_gate",p)

    ev={
      "benchmark":"FATHER RUNTIME EXECUTION MVP-04",
      "checks":rows
    }
    path=BASE/"evidence/runtime_execution_mvp04.json"
    path.write_text(json.dumps(ev,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT:","PASS" if ok else "FAIL")
    print("EVIDENCE:",path)
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
