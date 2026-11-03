import json
import urllib.request
from pathlib import Path

from father.core.assembler import AgentAssembler
from father.core.brain_experiments import BrainExperimentRunner
from father.core.hybrid_knowledge import HybridFolderKnowledge, OllamaEmbeddingClient
from father.core.io import ApiInputAdapter

BASE=Path(__file__).resolve().parent
CFG=json.loads((BASE/"config/experiments/brain_swap_hybrid.json").read_text(encoding="utf-8"))
BASE_URL="http://127.0.0.1:11434"
MODEL=CFG["embedding_model"]

evidence={
    "stage":"FATHER Hybrid Brain Lab v1 / Stage 25",
    "goal":"prove hybrid RAG plus automatic brain swapping under frozen hybrid context",
    "checks":[],
    "cases":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

def model_names():
    with urllib.request.urlopen(BASE_URL+"/api/tags",timeout=20) as r:
        payload=json.loads(r.read().decode("utf-8"))
    return {x.get("name") or x.get("model") for x in payload.get("models",[])}

def ensure_embedding_model():
    names=model_names()
    if MODEL in names or MODEL+":latest" in names:
        return {"installed":True,"pulled":False,"model":MODEL}
    body=json.dumps({"model":MODEL,"stream":False}).encode("utf-8")
    req=urllib.request.Request(
        BASE_URL+"/api/pull",
        data=body,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req,timeout=1800) as r:
        reply=json.loads(r.read().decode("utf-8"))
    names=model_names()
    return {
        "installed":MODEL in names or MODEL+":latest" in names,
        "pulled":True,
        "model":MODEL,
        "status":reply.get("status")
    }

print("=== HYBRID RAG PREFLIGHT ===")
model_status=ensure_embedding_model()
add("embedding_model_ready",model_status["installed"],model_status)

embedder=OllamaEmbeddingClient(model=MODEL,base_url=BASE_URL)
knowledge=HybridFolderKnowledge(
    BASE/CFG["rag_corpus"],
    embedder,
    chunk_chars=1200,
    semantic_weight=CFG["semantic_weight"],
    lexical_weight=CFG["lexical_weight"]
)
index_status=knowledge.build_index()
health=knowledge.health()
add("hybrid_rag_ready",
    health["status"]=="ok"
    and health["adapter"]=="hybrid-folder"
    and index_status["chunks"]>=3,
    {"index":index_status,"health":health}
)

print("\n=== ASSEMBLE ONE AGENT / HOT-SWAP KNOWLEDGE SLOT ===")
assembler=AgentAssembler(BASE)
agent,_=assembler.assemble(BASE/CFG["agent_manifest"])
old_knowledge=agent.knowledge.health()
agent.knowledge=knowledge
add("knowledge_slot_hot_swapped",
    old_knowledge.get("adapter")=="folder"
    and agent.knowledge.health().get("adapter")=="hybrid-folder",
    {"old":old_knowledge,"new":agent.knowledge.health()}
)

api=ApiInputAdapter()
runner=BrainExperimentRunner(assembler,agent,top_k=CFG["top_k"])
original_brain=agent.brain.brain_id

print("\n=== MULTI-TASK BRAIN EXPERIMENTS ===")
for task in CFG["tasks"]:
    event=api.normalize({
        "type":task["task_type"],
        "content":task["prompt"],
        "metadata":{"stage":25,"test_id":task["id"]}
    })
    case=runner.run_case(
        event,
        task["task_type"],
        task["rubric"],
        CFG["brains"]
    )
    case["test_id"]=task["id"]
    evidence["cases"].append(case)

    modes=case["frozen_context"]["knowledge_modes"]
    add("hybrid_context_"+task["id"],
        case["frozen_context"]["knowledge_hits"]>0
        and "hybrid-semantic-lexical" in modes,
        {
            "knowledge_hits":case["frozen_context"]["knowledge_hits"],
            "knowledge_sources":case["frozen_context"]["knowledge_sources"],
            "knowledge_modes":modes
        }
    )

    add("all_brains_ran_"+task["id"],
        len(case["results"])==len(CFG["brains"]),
        {
            "winner":case["winner"],
            "ranking":[
                {
                    "rank":x["rank"],
                    "brain_id":x["brain_id"],
                    "quality":x["quality"]["score"],
                    "passed":x["quality"]["passed"],
                    "latency_ms":x["latency_ms"],
                    "ok":x["ok"]
                }
                for x in case["results"]
            ]
        }
    )

summary=runner.aggregate(evidence["cases"])
evidence["summary"]=summary

print("\n=== AGGREGATE RANKING ===")
for row in summary["ranking"]:
    print("RANK",row["rank"],json.dumps(row,ensure_ascii=False))

add("task_suite_ranking_created",
    len(summary["ranking"])==len(CFG["brains"]) and bool(summary["winner"]),
    summary
)
add("original_brain_restored",
    agent.brain.brain_id==original_brain,
    {"before":original_brain,"after":agent.brain.brain_id}
)

print("\n=== ROUTING RECOMMENDATIONS FROM EXPERIMENT ===")
recommendations={}
for case in evidence["cases"]:
    recommendations[case["test_id"]]=case["winner"]
evidence["recommendations"]=recommendations
add("per_task_winners_recorded",
    len(recommendations)==len(CFG["tasks"]),
    recommendations
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage25_hybrid_brain_lab.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nWINNER:",summary["winner"])
print("RESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
