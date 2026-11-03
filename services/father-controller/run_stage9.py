import json
from pathlib import Path

from father.core.agent_zoo import AgentZoo
from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter
from father.core.scoring import score_response

BASE=Path(__file__).resolve().parent
zoo=AgentZoo(BASE/"config/agents")
assembler=AgentAssembler(BASE)
api=ApiInputAdapter()

evidence={
    "stage":"FATHER Chassis v1.8 / Stage 9",
    "goal":"prove Agent Zoo registry and multi-agent assembly from one chassis",
    "checks":[],
    "agents":[],
    "runs":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))

print("=== AGENT ZOO REGISTRY ===")
health=zoo.health()
add("agent_zoo_health",health["status"]=="ok" and health["agents"]>=5,health)

rows=zoo.manifests()
for row in rows:
    print(json.dumps(row,ensure_ascii=False))
evidence["agents"]=rows

required_ids={
    "father-lab-agent",
    "father-general-agent",
    "father-ib-agent",
    "father-edge-agent",
    "father-coder-agent"
}
ids={x["agent_id"] for x in rows}
add("required_agents_registered",required_ids.issubset(ids),{
    "required":sorted(required_ids),
    "registered":sorted(ids),
    "missing":sorted(required_ids-ids)
})

print("\n=== ASSEMBLE ALL AGENTS ===")
assembled={}
for row in rows:
    agent,manifest=assembler.assemble(row["manifest_path"])
    assembled[row["agent_id"]]=agent
    ok=(
        agent.agent_id==row["agent_id"]
        and agent.brain.brain_id==row["brain_id"]
        and agent.competency_id in {row["competency_id"],"ib-demo"}
    )
    add("assemble_"+row["agent_id"],ok,{
        "agent_id":agent.agent_id,
        "brain_id":agent.brain.brain_id,
        "competency_id":agent.competency_id
    })

print("\n=== EXECUTE ROLE PROFILES ===")
cases=[
    {
        "agent_id":"father-general-agent",
        "pack":"generic",
        "test_index":0
    },
    {
        "agent_id":"father-ib-agent",
        "pack":"ib_demo",
        "test_index":0
    },
    {
        "agent_id":"father-edge-agent",
        "pack":"generic",
        "test_index":1
    },
    {
        "agent_id":"father-coder-agent",
        "pack":"generic",
        "test_index":0
    }
]

for case in cases:
    agent=assembled[case["agent_id"]]
    pack=assembler.competency(case["pack"])
    test=pack.tests[case["test_index"]]
    result=agent.run(api.normalize({"content":test["prompt"]}))
    quality=score_response(result.content,test["rubric"])
    row={
        "agent_id":case["agent_id"],
        "brain_id":result.metadata.get("brain_id"),
        "competency_id":result.metadata.get("competency_id"),
        "knowledge_hits":result.metadata.get("knowledge_hits"),
        "ok":result.ok,
        "quality_score":quality["score"],
        "quality_passed":quality["passed"],
        "response":result.content
    }
    evidence["runs"].append(row)
    print(json.dumps(row,ensure_ascii=False))
    add(
        "run_"+case["agent_id"],
        result.ok and quality["passed"] and (result.metadata.get("knowledge_hits") or 0)>0,
        row
    )

print("\n=== COMMON CHASSIS CONTRACT ===")
contract_ok=all(
    hasattr(agent,"run")
    and hasattr(agent,"swap_brain")
    and hasattr(agent,"apply_competency")
    and hasattr(agent,"call_tool")
    for agent in assembled.values()
)
add("common_chassis_contract",contract_ok,{
    "agents":sorted(assembled.keys()),
    "methods":["run","swap_brain","apply_competency","call_tool"]
})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage9_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
