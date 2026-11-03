import json
import urllib.request
from pathlib import Path

from father.core.assembler import AgentAssembler
from father.core.hybrid_knowledge import HybridFolderKnowledge, OllamaEmbeddingClient
from father.core.io import ApiInputAdapter
from father.core.unified_runtime import UnifiedAgentRuntime
from father.contracts.types import KnowledgeQuery

BASE=Path(__file__).resolve().parent
PROFILE=json.loads((BASE/"config/runtime_profiles/hybrid_rag.json").read_text(encoding="utf-8"))
MODEL=PROFILE["retrieval"]["embedding_model"]
BASE_URL="http://127.0.0.1:11434"

evidence={
    "stage":"FATHER Unified Agent v3.2 / Stage 23",
    "goal":"prove real semantic + lexical hybrid RAG in the same agent runtime",
    "profile":PROFILE,
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

def tags():
    with urllib.request.urlopen(BASE_URL+"/api/tags",timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def ensure_model(model):
    payload=tags()
    names={x.get("name") or x.get("model") for x in payload.get("models",[])}
    if model in names or model+":latest" in names:
        return {"installed":True,"pulled":False,"model":model}
    body=json.dumps({"model":model,"stream":False}).encode("utf-8")
    req=urllib.request.Request(
        BASE_URL+"/api/pull",
        data=body,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req,timeout=1800) as r:
        reply=json.loads(r.read().decode("utf-8"))
    payload=tags()
    names={x.get("name") or x.get("model") for x in payload.get("models",[])}
    ok=model in names or model+":latest" in names
    return {"installed":ok,"pulled":True,"model":model,"reply":reply}

print("=== EMBEDDING MODEL PREFLIGHT ===")
model_status=ensure_model(MODEL)
add("embedding_model_ready",model_status["installed"],model_status)

print("\n=== BUILD HYBRID INDEX ===")
embedder=OllamaEmbeddingClient(model=MODEL,base_url=BASE_URL)
knowledge=HybridFolderKnowledge(
    BASE/"config/rag_stage23",
    embedder,
    chunk_chars=1200,
    semantic_weight=PROFILE["retrieval"]["semantic_weight"],
    lexical_weight=PROFILE["retrieval"]["lexical_weight"]
)
index_status=knowledge.build_index()
health=knowledge.health()
add("hybrid_index_built",
    index_status["chunks"]>=3 and health["status"]=="ok",
    {"index":index_status,"health":health}
)

print("\n=== SEMANTIC RETRIEVAL TESTS ===")
tests=[
    (
        "brain_slot",
        "Как заменить нейросеть внутри агента без переделки остальной архитектуры?",
        "brain_slot.md"
    ),
    (
        "knowledge_slot",
        "Как агент получает релевантные сведения из документов перед генерацией ответа?",
        "knowledge_slot.md"
    ),
    (
        "industrial",
        "Почему языковую модель нельзя напрямую подключать к исполнительному механизму?",
        "industrial.md"
    )
]

for name,query,expected_file in tests:
    result=knowledge.search(KnowledgeQuery(text=query,top_k=3))
    top=result.items[0] if result.items else {}
    add("hybrid_retrieval_"+name,
        bool(top)
        and top.get("retrieval_mode")=="hybrid-semantic-lexical"
        and Path(top.get("source","")).name==expected_file
        and top.get("semantic_score",0)>0,
        {
            "query":query,
            "top_source":top.get("source"),
            "semantic_score":top.get("semantic_score"),
            "lexical_score":top.get("lexical_score"),
            "hybrid_score":top.get("score"),
            "mode":top.get("retrieval_mode")
        }
    )

print("\n=== PLUG HYBRID RAG INTO SAME AGENT ===")
assembler=AgentAssembler(BASE)
agent,_=assembler.assemble(BASE/PROFILE["agent_manifest"])
old_adapter=agent.knowledge.health().get("adapter")
agent.knowledge=knowledge
new_adapter=agent.knowledge.health().get("adapter")
add("knowledge_slot_hot_swapped",
    old_adapter=="folder" and new_adapter=="hybrid-folder",
    {"old":old_adapter,"new":new_adapter}
)

runtime=UnifiedAgentRuntime(agent,top_k=PROFILE["retrieval"]["top_k"])
api=ApiInputAdapter()
event=api.normalize({
    "type":"architecture",
    "content":"Как в FATHER заменить одну LLM на другую без переписывания агента?",
    "metadata":{"stage":23}
})
run=runtime.run(event,"architecture")
add("agent_runs_with_hybrid_rag",
    run["ok"]
    and run["knowledge_hits"]>0
    and "hybrid-semantic-lexical" in run["knowledge_modes"]
    and bool(run["content"]),
    {
        "ok":run["ok"],
        "brain_id":run["brain_id"],
        "knowledge_hits":run["knowledge_hits"],
        "knowledge_sources":run["knowledge_sources"],
        "knowledge_modes":run["knowledge_modes"],
        "content_chars":len(run["content"] or "")
    }
)

add("context_bus_carries_rag",
    bool(run["envelope"]["knowledge"])
    and run["envelope"]["knowledge"][0].get("embedding_model")==MODEL,
    {
        "knowledge_items":len(run["envelope"]["knowledge"]),
        "embedding_model":run["envelope"]["knowledge"][0].get("embedding_model") if run["envelope"]["knowledge"] else None
    }
)

print("\n=== MATURITY LABEL ===")
add("rag_maturity_declared",
    PROFILE["retrieval"]["mode"]=="hybrid-semantic-lexical"
    and PROFILE["retrieval"]["persistent_vector_db"] is False,
    PROFILE["retrieval"]
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage23_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
