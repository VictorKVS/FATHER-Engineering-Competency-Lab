import json
from pathlib import Path

from father.core.escalating_runtime import EscalatingRuntime

BASE=Path(__file__).resolve().parent
SPEC={
  "product_id":"father-escalation-mvp05",
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

def compact(x):
    return {
      "ok":x.get("ok"),
      "escalated":x.get("escalated"),
      "initial_brain":x.get("initial_brain"),
      "final_brain":x.get("final_brain"),
      "escalation_reason":x.get("escalation_reason"),
      "attempts":x.get("attempts")
    }

def main():
    r=EscalatingRuntime(BASE)
    rows=[]; ok=True

    x=r.run(
      {"role":"text_analyst","complexity":2,
       "text":"Кратко объясни принцип: агент не равен модели."},
      SPEC,gpu_temp_c=70,
      acceptance={"min_chars":1}
    )
    ok &= add(rows,"accepted_qwen3b_does_not_escalate",
              x.get("ok") and not x.get("escalated") and x.get("final_brain")=="qwen-analysis-fast",
              compact(x))

    x=r.run(
      {"role":"text_analyst","complexity":2,
       "text":"Объясни архитектурный принцип FATHER: агент не равен модели."},
      SPEC,gpu_temp_c=70,
      acceptance={"min_chars":5000}
    )
    ok &= add(rows,"rejected_qwen3b_escalates_to_qwen7b",
              x.get("escalated") and x.get("initial_brain")=="qwen-analysis-fast" and x.get("final_brain")=="qwen-analysis",
              compact(x))

    attempts=x.get("attempts") or []
    ok &= add(rows,"telemetry_records_both_attempts",
              len(attempts)==2 and all(a.get("latency_ms") is not None for a in attempts)
              and all(a.get("content_chars") is not None for a in attempts),
              {"attempts":attempts})

    p=r.router.plan(
      {"role":"text_analyst","complexity":2,"text":"анализ"},
      SPEC,gpu_temp_c=91
    )
    ok &= add(rows,"thermal_gate_still_precedes_execution",
              (not p.get("ok")) and p.get("reason")=="thermal_gate",p)

    ev={
      "benchmark":"FATHER EXECUTION TELEMETRY + ESCALATION MVP-05",
      "semantic_judge":"NOT_IN_THIS_MVP",
      "checks":rows
    }
    path=BASE/"evidence/execution_escalation_mvp05.json"
    path.write_text(json.dumps(ev,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT:","PASS" if ok else "FAIL")
    print("EVIDENCE:",path)
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
