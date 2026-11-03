import json
from pathlib import Path

from father.core.agent_zoo import AgentZoo
from father.core.agent_router import AgentRouter
from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter
from father.core.scoring import score_response

BASE=Path(__file__).resolve().parent
zoo=AgentZoo(BASE/"config/agents")
router=AgentRouter(BASE/"config/agent_routes.json",zoo)
assembler=AgentAssembler(BASE)
api=ApiInputAdapter()

evidence={
    "stage":"FATHER Chassis v1.9 / Stage 10",
    "goal":"prove deterministic task routing from normalized event to Agent Zoo profile",
    "checks":[],
    "routes":[],
    "runs":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== ROUTER HEALTH ===")
health=router.health()
add("router_health",health["status"]=="ok",health)

cases=[
    {
        "task_type":"architecture",
        "expected_agent":"father-general-agent",
        "pack":"generic",
        "test_index":0
    },
    {
        "task_type":"ib-knowledge",
        "expected_agent":"father-ib-agent",
        "pack":"ib_demo",
        "test_index":0
    },
    {
        "task_type":"coding",
        "expected_agent":"father-coder-agent",
        "pack":"generic",
        "test_index":0
    },
    {
        "task_type":"edge",
        "expected_agent":"father-edge-agent",
        "pack":"generic",
        "test_index":1
    }
]

print("\n=== ROUTE + EXECUTE ===")
for case in cases:
    route=router.route(case["task_type"])
    evidence["routes"].append(route)
    route_ok=route["agent_id"]==case["expected_agent"] and route["fallback"] is False
    add("route_"+case["task_type"],route_ok,route)

    agent,_=assembler.assemble(route["manifest_path"])
    pack=assembler.competency(case["pack"])
    test=pack.tests[case["test_index"]]
    event=api.normalize({
        "type":case["task_type"],
        "content":test["prompt"],
        "metadata":{"task_type":case["task_type"]}
    })
    result=agent.run(event)
    quality=score_response(result.content,test["rubric"])
    run={
        "task_type":case["task_type"],
        "routed_agent":route["agent_id"],
        "brain_id":result.metadata.get("brain_id"),
        "competency_id":result.metadata.get("competency_id"),
        "knowledge_hits":result.metadata.get("knowledge_hits"),
        "ok":result.ok,
        "quality_score":quality["score"],
        "quality_passed":quality["passed"],
        "response":result.content
    }
    evidence["runs"].append(run)
    print(json.dumps(run,ensure_ascii=False))
    add(
        "execute_"+case["task_type"],
        result.ok and quality["passed"] and (result.metadata.get("knowledge_hits") or 0)>0,
        run
    )

print("\n=== DEFAULT ROUTE ===")
default_route=router.route("unknown-task")
default_ok=default_route["agent_id"]=="father-general-agent" and default_route["fallback"] is True
add("default_route_fallback",default_ok,default_route)

print("\n=== ROUTING TRACEABILITY ===")
trace_ok=all(
    r.get("task_type") and r.get("agent_id") and r.get("manifest_path")
    for r in evidence["routes"]
)
add("routing_traceability",trace_ok,{
    "route_count":len(evidence["routes"]),
    "routes":evidence["routes"]
})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage10_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
