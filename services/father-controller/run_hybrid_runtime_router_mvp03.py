import json
from pathlib import Path

from father.core.hybrid_runtime_router import HybridRuntimeRouter

BASE=Path(__file__).resolve().parent
SPEC={
  "product_id":"father-runtime-router-mvp03",
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

def main():
    r=HybridRuntimeRouter(BASE)
    rows=[]; ok=True

    p=r.plan({"role":"text_analyst","complexity":2,"text":"анализ книги"},SPEC,gpu_temp_c=70)
    ok &= add(rows,"runtime_routine_analysis_maps_to_qwen3b",
              p.get("ok") and p.get("brain_id")=="qwen-analysis-fast" and not p.get("fallback_used"),p)

    b=r.build({"role":"text_analyst","complexity":2,"text":"анализ книги"},SPEC,gpu_temp_c=70)
    br=(b.get("product") or {}).get("report",{})
    ok &= add(rows,"factory_builds_qwen3b_agent",
              b.get("ok") and br.get("brain_id")=="qwen-analysis-fast",br)

    p=r.plan({"role":"text_analyst","complexity":4,"text":"глубокий анализ причин"},SPEC,gpu_temp_c=70)
    ok &= add(rows,"runtime_complex_analysis_maps_to_qwen7b",
              p.get("ok") and p.get("brain_id")=="qwen-analysis" and not p.get("fallback_used"),p)

    p=r.plan({"role":"edge_fast","complexity":1,"text":"коротко перепиши фразу"},SPEC,gpu_temp_c=70)
    ok &= add(rows,"runtime_edge_maps_to_llama1b",
              p.get("ok") and p.get("brain_id")=="llama-small" and not p.get("fallback_used"),p)

    p=r.plan({"role":"coding","specialization":"coding","complexity":3,"text":"исправь python код"},SPEC,gpu_temp_c=70)
    ok &= add(rows,"unpromoted_coding_uses_stage29_fallback",
              p.get("ok") and p.get("fallback_used") and p.get("brain_id")=="qwen-coder",p)

    p=r.plan({"role":"text_analyst","complexity":2,"text":"анализ"},SPEC,gpu_temp_c=91)
    ok &= add(rows,"thermal_block_is_not_bypassed",
              (not p.get("ok")) and p.get("reason")=="thermal_gate",p)

    ev={
      "benchmark":"FATHER HYBRID RUNTIME ROUTER MVP-03",
      "promoted_roles":["text_analyst","edge_fast"],
      "fallback":"Stage29",
      "checks":rows
    }
    path=BASE/"evidence/hybrid_runtime_router_mvp03.json"
    path.write_text(json.dumps(ev,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT:","PASS" if ok else "FAIL")
    print("EVIDENCE:",path)
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
