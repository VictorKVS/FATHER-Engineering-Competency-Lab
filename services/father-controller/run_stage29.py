import json
from pathlib import Path

from father.core.adaptive_brain_router import AdaptiveBrainRouter
from father.core.block_registry import BlockRegistry
from father.core.model_applicability import ModelApplicabilityEngine
from father.core.io import ApiInputAdapter

BASE=Path(__file__).resolve().parent
router=AdaptiveBrainRouter(BASE)
registry=BlockRegistry(BASE/"config/blocks.json")
engine=ModelApplicabilityEngine(BASE/"config/model_knowledge_base.json")
base_spec=router.factory.load_spec("config/products/father_general_single.json")
api=ApiInputAdapter()

evidence={
    "stage":"FATHER Adaptive Brain Router / Stage 29",
    "goal":"prove task-aware brain selection connected to registry and product factory",
    "checks":[],
    "cases":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== FOUNDATION CHECKS ===")
reg_health=registry.health()
add("block_registry_ready",
    reg_health["status"]=="ok" and reg_health["blocks"]>=14,
    reg_health
)

kb_ok=engine.data.get("kb_version")=="1.0" and len(engine.models)>=6
add("model_knowledge_base_ready",
    kb_ok,
    {"kb_version":engine.data.get("kb_version"),"models":sorted(engine.models)}
)

cases=[
    {
        "id":"simple-edge",
        "task":{
            "text":"Кратко перепиши этот текст для локального легкого помощника.",
            "complexity":1,
            "specialization":"general",
            "modality":"text"
        },
        "expected":"llama-small",
        "execute":True
    },
    {
        "id":"general-rag",
        "task":{
            "text":"Объясни, как агент использует базу знаний и RAG для ответа.",
            "complexity":2,
            "specialization":"rag",
            "modality":"text"
        },
        "expected":"qwen-analysis",
        "execute":True
    },
    {
        "id":"coding",
        "task":{
            "text":"Напиши короткую Python функцию сложения двух чисел и объясни код.",
            "complexity":3,
            "specialization":"coding",
            "modality":"text"
        },
        "expected":"qwen-coder",
        "execute":True
    },
    {
        "id":"deep-reasoning",
        "task":{
            "text":"Сравни два архитектурных сценария и проведи многошаговое рассуждение о компромиссах.",
            "complexity":4,
            "specialization":"reasoning",
            "modality":"text"
        },
        "expected":"deepseek-reasoning",
        "execute":True
    }
]

print("\n=== ADAPTIVE ROUTING + FACTORY BUILD ===")
for case in cases:
    plan=router.plan(case["task"],base_spec)
    selected=(plan.get("selected") or {}).get("brain_id")

    add("route_"+case["id"],
        plan.get("ok") is True and selected==case["expected"],
        {
            "expected":case["expected"],
            "selected":selected,
            "task_profile":plan.get("task_profile"),
            "reasons":(plan.get("selected") or {}).get("reasons"),
            "score":(plan.get("selected") or {}).get("score"),
            "validation":plan.get("validation")
        }
    )

    built=router.build(case["task"],base_spec)
    product=built["product"]
    report=product["report"]

    add("build_"+case["id"],
        report["status"]=="ready"
        and report["brain_id"]==case["expected"]
        and report["registry"]["status"]=="ok",
        report
    )

    run_result=None
    if case["execute"]:
        event=api.normalize({
            "type":"architecture",
            "content":case["task"]["text"],
            "metadata":{"stage":29,"case_id":case["id"]}
        })
        run_result=product["runtime"].run(event,case["task"].get("specialization","message"))
        add("execute_"+case["id"],
            run_result["ok"]
            and run_result["brain_id"]==case["expected"]
            and bool(run_result["content"]),
            {
                "ok":run_result["ok"],
                "brain_id":run_result["brain_id"],
                "knowledge_hits":run_result["knowledge_hits"],
                "content_chars":len(run_result["content"] or ""),
                "error":run_result.get("error")
            }
        )

    evidence["cases"].append({
        "id":case["id"],
        "task":case["task"],
        "selected":selected,
        "plan":{
            "task_profile":plan.get("task_profile"),
            "selected":plan.get("selected"),
            "top3":plan.get("ranking",[])[:3]
        },
        "build_report":report,
        "execution":{
            "ok":run_result["ok"],
            "brain_id":run_result["brain_id"],
            "content":run_result["content"],
            "knowledge_hits":run_result["knowledge_hits"],
            "error":run_result.get("error")
        } if run_result else None
    })

print("\n=== VISION BOUNDARY ===")
vision_task={
    "text":"Проанализируй изображение промышленной схемы.",
    "complexity":2,
    "specialization":"vision",
    "modality":"vision"
}
vision_plan=router.plan(vision_task,base_spec)
add("unregistered_vision_is_blocked",
    vision_plan.get("ok") is False
    and vision_plan.get("reason")=="no_compatible_registered_brain",
    vision_plan
)

print("\n=== EXPLAINABILITY ===")
all_explained=all(
    case["plan"]["selected"]
    and case["plan"]["selected"].get("reasons")
    and case["plan"]["selected"].get("score") is not None
    for case in evidence["cases"]
)
add("every_route_is_explainable",
    all_explained,
    {
        x["id"]:{
            "brain":x["selected"],
            "reasons":x["plan"]["selected"]["reasons"],
            "score":x["plan"]["selected"]["score"]
        }
        for x in evidence["cases"]
    }
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage29_adaptive_brain_router.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("CYCLE: 0-29 COMPLETE" if release else "CYCLE: 0-29 NOT COMPLETE")
raise SystemExit(0 if release else 1)
