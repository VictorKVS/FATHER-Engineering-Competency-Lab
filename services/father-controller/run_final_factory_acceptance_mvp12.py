import json
from pathlib import Path

from father.core.hybrid_runtime_router import HybridRuntimeRouter
from father.core.semantic_escalation_runtime import SemanticEscalationRuntime

BASE = Path(__file__).resolve().parent

SPEC = {
  "product_id": "father-final-acceptance-v1",
  "agent_manifest": "config/agents/father_general.json",
  "brain_id": "qwen-analysis",
  "competency_id": "generic",
  "inputs": ["api", "file"],
  "outputs": ["json", "file"],
  "knowledge": {"adapter": "folder"},
  "retrieval": {"top_k": 5},
  "tools": "default",
  "context_bus": True,
}

CONTEXT = """FATHER — модульная AI-фабрика.
Агент и модель разделены.
Модель является заменяемым Brain-слотом.
Роутер выбирает подходящий brain по роли и сложности.
Результат проходит acceptance и сохраняет evidence."""
CLAIMS = [
    "FATHER разделяет агента и модель.",
    "Модель является заменяемым Brain-слотом агента.",
    "Роутер выбирает подходящий brain по роли и сложности.",
]

def add(rows,name,passed,details):
    rows.append({"name":name,"passed":bool(passed),"details":details})
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return bool(passed)

def main():
    rows=[]
    ok=True

    router=HybridRuntimeRouter(BASE)

    # 1. Routine text analyst must use economical 3B.
    routine=router.plan({"role":"text_analyst","complexity":2,"text":"Кратко проанализируй архитектуру."},gpu_temp_c=70)
    ok &= add(rows,"routine_text_routes_to_3b",
              routine.get("ok") and routine.get("brain_id")=="qwen-analysis-fast",
              routine)

    # 2. Complex text analyst must escalate to 7B.
    complex_plan=router.plan({"role":"text_analyst","complexity":4,"text":"Проведи глубокий анализ архитектуры."},gpu_temp_c=70)
    ok &= add(rows,"complex_text_routes_to_7b",
              complex_plan.get("ok") and complex_plan.get("brain_id")=="qwen-analysis",
              complex_plan)

    # 3. Coding role remains conditional but routable.
    coding=router.plan({"role":"coding","complexity":3,"text":"Напиши безопасную функцию Python."},gpu_temp_c=70)
    ok &= add(rows,"coding_role_is_routable",
              coding.get("ok") and coding.get("brain_id")=="qwen-coder",
              coding)

    # 4. Edge-fast remains routable.
    edge=router.plan({"role":"edge_fast","complexity":1,"text":"Сократи фразу."},gpu_temp_c=70)
    ok &= add(rows,"edge_routes_to_llama",
              edge.get("ok") and edge.get("brain_id")=="llama-small",
              edge)

    # 5. Thermal gate must block execution plans.
    hot=router.plan({"role":"text_analyst","complexity":2,"text":"Анализ."},gpu_temp_c=91)
    ok &= add(rows,"thermal_gate_blocks_hot_runtime",
              (not hot.get("ok")) and hot.get("reason")=="thermal_gate",
              hot)

    # 6. Real semantic runtime end-to-end.
    sem=SemanticEscalationRuntime(BASE)
    result=sem.run(
        {"role":"text_analyst","complexity":2,"text":"Объясни, почему в FATHER агент не равен модели."},
        SPEC,
        CONTEXT,
        CLAIMS,
        gpu_temp_c=70,
    )
    ok &= add(rows,"real_semantic_runtime_accepts_grounded_answer",
              result.get("ok") and result.get("status")=="ACCEPTED",
              {
                  "ok":result.get("ok"),
                  "status":result.get("status"),
                  "initial_brain":result.get("initial_brain"),
                  "final_brain":result.get("final_brain"),
                  "escalated":result.get("escalated"),
              })

    # 7. Evidence artifacts from role qualification must exist.
    required=[
        "evidence/semantic_escalation_runtime_mvp07.json",
        "evidence/coding_role_bench_mvp08.json",
        "evidence/reasoning_role_bench_mvp09.json",
        "evidence/creative_role_bench_mvp10.json",
        "evidence/vision_role_bench_mvp11.json",
    ]
    missing=[x for x in required if not (BASE/x).exists()]
    ok &= add(rows,"role_evidence_chain_present",not missing,{"missing":missing})

    # 8. Factory release pipeline evidence from MVP06 must exist.
    release_evidence=BASE/"evidence/factory_mvp06_release_line.json"
    ok &= add(rows,"release_pipeline_evidence_present",release_evidence.exists(),{"path":str(release_evidence)})

    report={
        "benchmark":"FATHER FINAL FACTORY ACCEPTANCE MVP-12",
        "goal_progress":{"before_percent":96,"target_percent":100},
        "principle":"whole product must prove operational behavior before factory is declared ready",
        "checks":rows,
        "summary":{
            "passed":sum(1 for x in rows if x["passed"]),
            "failed":sum(1 for x in rows if not x["passed"]),
            "total":len(rows),
        },
        "factory_ready":bool(ok),
        "role_status":{
            "text_analyst":"QUALIFIED",
            "reasoning":"QUALIFIED",
            "coding":"CONDITIONAL",
            "creative":"QUALIFIED_CONDITIONAL",
            "vision":"QUALIFIED",
        },
    }
    path=BASE/"evidence/final_factory_acceptance_mvp12.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

    print("=== FINAL FACTORY DECISION ===")
    print("RESULT:","PASS" if ok else "FAIL")
    print("FACTORY_READY:",bool(ok))
    print("EVIDENCE:",path)
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
