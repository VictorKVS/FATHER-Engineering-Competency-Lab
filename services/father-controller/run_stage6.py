import json, time
from pathlib import Path

from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter
from father.core.knowledge import FolderKnowledge
from father.core.model_zoo import ModelZooDB
from father.core.scoring import score_response
from father.contracts.types import KnowledgeQuery

BASE=Path(__file__).resolve().parent
brains_cfg=json.loads((BASE/"config/brains.json").read_text(encoding="utf-8"))["brains"]
assembler=AgentAssembler(BASE)
zoo=ModelZooDB(BASE/"data/model_zoo.db")
zoo.register_models(brains_cfg)
api=ApiInputAdapter()

evidence={
    "stage":"FATHER Chassis v1.5 / Stage 6",
    "goal":"prove Knowledge Slot / Competency Pack delivery before ranking brains",
    "checks":[],
    "runs":[]
}

def add_check(name, passed, details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"), name, json.dumps(details,ensure_ascii=False))
    return bool(passed)

print("=== KNOWLEDGE SLOT PROBE ===")
ib=assembler.competency("ib_demo")
kb=FolderKnowledge(ib.knowledge_dir,fallback_on_empty=True)
probe=kb.search(KnowledgeQuery(text="Перечисли нормативные документы в подключенной БЗ.",top_k=5))
probe_text="\n".join(x.get("text","") for x in probe.items)

expected=["152-ФЗ","187-ФЗ","149-ФЗ","1119","235","239","378"]
probe_ok=len(probe.items)>0 and all(x.lower() in probe_text.lower() for x in expected)
add_check("knowledge_probe",probe_ok,{
    "hits":len(probe.items),
    "modes":[x.get("retrieval_mode") for x in probe.items],
    "sources":[x.get("source") for x in probe.items],
    "expected_present":{x:(x.lower() in probe_text.lower()) for x in expected}
})

print("\n=== IB COMPETENCY BENCHMARK ===")
ib_passes=0
for test in ib.tests:
    for brain_id in brains_cfg:
        agent,_=assembler.assemble(BASE/"config/agents/father_lab.json")
        agent.apply_competency(ib,FolderKnowledge(ib.knowledge_dir,fallback_on_empty=True))
        agent.swap_brain(assembler.brain(brain_id))

        t0=time.perf_counter()
        result=agent.run(api.normalize({"content":test["prompt"]}))
        elapsed=int((time.perf_counter()-t0)*1000)
        quality=score_response(result.content,test["rubric"])
        if quality["passed"]:
            ib_passes += 1

        zoo.record_run(
            brain_id,agent.agent_id,agent.competency_id,
            "stage6-"+test["id"],test["task_type"],result,elapsed,quality
        )

        row={
            "task_id":test["id"],
            "brain_id":brain_id,
            "ok":result.ok,
            "quality_score":quality["score"],
            "quality_passed":quality["passed"],
            "knowledge_hits":result.metadata.get("knowledge_hits"),
            "knowledge_modes":result.metadata.get("knowledge_modes"),
            "elapsed_ms":elapsed,
            "response":result.content
        }
        evidence["runs"].append(row)
        print(json.dumps(row,ensure_ascii=False))

add_check("ib_at_least_one_model_passes",ib_passes>=1,{
    "passed_models":ib_passes,
    "total_models":len(brains_cfg)
})

all_delivery_ok=all(
    (r.get("knowledge_hits") or 0)>0
    for r in evidence["runs"]
)
add_check("knowledge_delivered_to_all_brains",all_delivery_ok,{
    "delivery":[
        {"brain_id":r["brain_id"],"hits":r["knowledge_hits"],"modes":r["knowledge_modes"]}
        for r in evidence["runs"]
    ]
})

ranking=zoo.ranking("ib-knowledge")
evidence["ib_ranking"]=ranking

all_ok=all(c["passed"] for c in evidence["checks"])
evidence["result"]="PASS" if all_ok else "FAIL"

(BASE/"evidence/stage6_evidence.json").write_text(
    json.dumps(evidence,ensure_ascii=False,indent=2),
    encoding="utf-8"
)

print("\n=== RANKING ib-knowledge ===")
print(json.dumps(ranking,ensure_ascii=False,indent=2))
print("\nRESULT:",evidence["result"])
print("EVIDENCE:",BASE/"evidence/stage6_evidence.json")
raise SystemExit(0 if all_ok else 1)
