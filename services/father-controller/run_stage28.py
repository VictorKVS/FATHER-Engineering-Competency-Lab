import json
from pathlib import Path

from father.core.model_applicability import ModelApplicabilityEngine

BASE=Path(__file__).resolve().parent
engine=ModelApplicabilityEngine(BASE/"config/model_knowledge_base.json")

evidence={
    "stage":"FATHER Model Knowledge Base / Stage 28",
    "goal":"prove task-aware LLM applicability knowledge and explainable model selection",
    "checks":[],
    "cases":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== KB STRUCTURE ===")
kb=engine.data
add("model_kb_loaded",
    kb.get("kb_version")=="1.0" and len(kb.get("models",{}))>=6,
    {"kb_version":kb.get("kb_version"),"models":sorted(kb.get("models",{}))}
)
add("decision_ladder_present",
    len(kb.get("decision_ladder",[]))>=5,
    {"stages":kb.get("decision_ladder",[])}
)

cases=[
    {
        "id":"general-rag",
        "task":{"text":"Сделай анализ документов из базы знаний и дай структурированный ответ","complexity":2,"specialization":"rag","modality":"text"},
        "expected":"qwen-analysis",
        "registered_only":True
    },
    {
        "id":"coding",
        "task":{"text":"Исправь Python API и объясни ошибку в коде","complexity":3,"specialization":"coding","modality":"text"},
        "expected":"qwen-coder",
        "registered_only":True
    },
    {
        "id":"deep-reasoning",
        "task":{"text":"Проведи сложное многошаговое рассуждение и сравни несколько архитектурных сценариев","complexity":4,"specialization":"reasoning","modality":"text"},
        "expected":"deepseek-reasoning",
        "registered_only":True
    },
    {
        "id":"simple-edge",
        "task":{"text":"Кратко перепиши текст для локального edge-агента","complexity":1,"specialization":"general","modality":"text"},
        "expected":"llama-small",
        "registered_only":True
    }
]

print("\n=== EXPLAINABLE MODEL SELECTION ===")
for case in cases:
    result=engine.choose(case["task"],registered_only=case["registered_only"])
    evidence["cases"].append({"id":case["id"],"task":case["task"],"result":result})
    selected=(result.get("selected") or {}).get("model_id")
    add("select_"+case["id"],
        selected==case["expected"],
        {
            "expected":case["expected"],
            "selected":selected,
            "task_profile":result["task_profile"],
            "top3":[
                {
                    "rank":x["rank"],
                    "model_id":x["model_id"],
                    "score":x["score"],
                    "reasons":x["reasons"],
                    "penalties":x["penalties"]
                }
                for x in result["ranking"][:3]
            ]
        }
    )

print("\n=== VISION BOUNDARY ===")
registered_vision=engine.choose({
    "text":"Проанализируй изображение схемы",
    "complexity":2,
    "specialization":"vision",
    "modality":"vision"
},registered_only=True)
add("vision_not_routed_to_text_brain",
    registered_vision["selected"] is None,
    registered_vision
)

all_vision=engine.choose({
    "text":"Проанализируй изображение схемы",
    "complexity":2,
    "specialization":"vision",
    "modality":"vision"
},registered_only=False)
selected_vision=all_vision.get("selected") or {}
add("vision_candidates_known",
    selected_vision.get("model_id") in {"qwen3-vl-vision","llava-vision"},
    {
        "selected":selected_vision.get("model_id"),
        "registered":selected_vision.get("brain_id") is not None,
        "ranking":[x["model_id"] for x in all_vision["ranking"]]
    }
)

print("\n=== LOCAL EVIDENCE LAYER ===")
qwen=kb["models"]["qwen-analysis"]
deep=kb["models"]["deepseek-reasoning"]
add("local_benchmark_evidence_attached",
    qwen.get("local_evidence",{}).get("stage24_rank")==1
    and deep.get("local_evidence",{}).get("stage24_rank")==4,
    {
        "qwen-analysis":qwen.get("local_evidence"),
        "deepseek-reasoning":deep.get("local_evidence")
    }
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage28_model_knowledge_base.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
