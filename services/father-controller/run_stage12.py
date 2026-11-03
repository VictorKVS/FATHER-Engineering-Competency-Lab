import json
from pathlib import Path

from father.core.agent_zoo import AgentZoo
from father.core.agent_router import AgentRouter
from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter
from father.core.policy import PolicyGate
from father.core.scoring import score_response
from father.core.workflow import WorkflowOrchestrator

BASE=Path(__file__).resolve().parent
zoo=AgentZoo(BASE/"config/agents")
router=AgentRouter(BASE/"config/agent_routes.json",zoo)
assembler=AgentAssembler(BASE)
policy=PolicyGate(BASE/"config/policies.json")
api=ApiInputAdapter()
audit_path=BASE/"evidence/stage12_audit.jsonl"
if audit_path.exists():
    audit_path.unlink()
workflow=WorkflowOrchestrator(router,assembler,audit_path,policy_gate=policy)

evidence={
    "stage":"FATHER Chassis v2.1 / Stage 12",
    "goal":"prove policy/UAG gate before agent and tool execution",
    "checks":[],
    "runs":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== POLICY HEALTH ===")
health=policy.health()
add("policy_health",health["status"]=="ok" and health["agents"]>=5,health)

print("\n=== ALLOW PATH: GENERAL + CALCULATOR ===")
generic=assembler.competency("generic")
test=generic.tests[0]
event=api.normalize({
    "type":"architecture",
    "content":test["prompt"],
    "metadata":{"stage":12}
})
state=workflow.run(
    event,
    "architecture",
    tool_call={"name":"calculator","arguments":{"a":8,"b":5,"op":"+"}}
)
quality=score_response(state["result"]["content"],test["rubric"]) if state.get("result") else {"passed":False}
evidence["runs"].append(state)
add("allow_general_calculator",state["status"]=="completed" and state["tool"]["result"]==13,{
    "status":state["status"],
    "tool":state["tool"],
    "policy":state["policy"]
})
add("allow_general_quality",quality["passed"],quality)

print("\n=== DENY TOOL PATH: IB + CALCULATOR ===")
ib=assembler.competency("ib_demo")
ib_event=api.normalize({
    "type":"ib-knowledge",
    "content":ib.tests[0]["prompt"],
    "metadata":{"stage":12}
})
denied_tool=workflow.run(
    ib_event,
    "ib-knowledge",
    tool_call={"name":"calculator","arguments":{"a":1,"b":1,"op":"+"}}
)
evidence["runs"].append(denied_tool)
stages=[x["stage"] for x in denied_tool["transitions"]]
add("deny_ib_calculator",denied_tool["status"]=="denied" and "tool" not in stages and "agent" not in stages,{
    "status":denied_tool["status"],
    "policy":denied_tool["policy"],
    "transitions":stages
})

print("\n=== DENY AGENT TASK PATH ===")
route_manifest=zoo.get("father-ib-agent")
agent_decision=policy.check_agent(route_manifest["agent_id"],"architecture")
add("deny_ib_wrong_task",agent_decision["allowed"] is False,agent_decision)

print("\n=== ALLOW IB WITHOUT TOOL ===")
ib_ok=workflow.run(ib_event,"ib-knowledge")
ib_quality=score_response(ib_ok["result"]["content"],ib.tests[0]["rubric"]) if ib_ok.get("result") else {"passed":False}
evidence["runs"].append(ib_ok)
add("allow_ib_task",ib_ok["status"]=="completed" and ib_quality["passed"],{
    "status":ib_ok["status"],
    "policy":ib_ok["policy"],
    "quality":ib_quality
})

print("\n=== POLICY AUDIT ===")
rows=[]
if audit_path.exists():
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
policy_rows=[x for x in rows if x["stage"].startswith("policy_")]
denied_rows=[x for x in policy_rows if x["status"]=="denied"]
add("policy_decisions_audited",len(policy_rows)>=4 and len(denied_rows)>=1,{
    "audit_path":str(audit_path),
    "policy_rows":len(policy_rows),
    "denied_rows":len(denied_rows)
})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage12_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("AUDIT:",audit_path)
raise SystemExit(0 if release else 1)
