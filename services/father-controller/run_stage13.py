import json
from pathlib import Path

from father.core.agent_zoo import AgentZoo
from father.core.agent_router import AgentRouter
from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter
from father.core.policy import PolicyGate
from father.core.sandbox import ExecutionSandbox
from father.core.scoring import score_response
from father.core.workflow import WorkflowOrchestrator

BASE=Path(__file__).resolve().parent
zoo=AgentZoo(BASE/"config/agents")
router=AgentRouter(BASE/"config/agent_routes.json",zoo)
assembler=AgentAssembler(BASE)
policy=PolicyGate(BASE/"config/policies.json")
sandbox=ExecutionSandbox(timeout_sec=2,max_text_chars=2000,max_abs_number=1000000)
api=ApiInputAdapter()

audit_path=BASE/"evidence/stage13_audit.jsonl"
if audit_path.exists():
    audit_path.unlink()

workflow=WorkflowOrchestrator(
    router,
    assembler,
    audit_path,
    policy_gate=policy,
    sandbox=sandbox
)

evidence={
    "stage":"FATHER Chassis v2.2 / Stage 13",
    "goal":"prove bootstrap execution sandbox after policy gate and before tool registry",
    "checks":[],
    "runs":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== SANDBOX HEALTH ===")
health=sandbox.health()
add("sandbox_health",health["status"]=="ok" and "calculator" in health["sandboxed_tools"],health)

print("\n=== ALLOW: VALID CALCULATOR ===")
generic=assembler.competency("generic")
test=generic.tests[0]
event=api.normalize({
    "type":"architecture",
    "content":test["prompt"],
    "metadata":{"stage":13}
})
state=workflow.run(
    event,
    "architecture",
    tool_call={"name":"calculator","arguments":{"a":9,"b":4,"op":"*"}}
)
quality=score_response(state["result"]["content"],test["rubric"]) if state.get("result") else {"passed":False}
evidence["runs"].append(state)
add("sandbox_allows_valid_tool",state["status"]=="completed" and state["tool"]["result"]==36,{
    "status":state["status"],
    "tool":state["tool"],
    "sandbox":state["sandbox"]
})
add("sandbox_valid_path_quality",quality["passed"],quality)

print("\n=== BLOCK: UNSANDBOXED TOOL ===")
state_unknown=workflow.run(
    event,
    "architecture",
    tool_call={"name":"get_time","arguments":{}}
)
evidence["runs"].append(state_unknown)
stages_unknown=[x["stage"] for x in state_unknown["transitions"]]
add("sandbox_blocks_unsandboxed_tool",
    state_unknown["status"]=="denied"
    and "sandbox" in stages_unknown
    and "tool" not in stages_unknown
    and "agent" not in stages_unknown,
    {
        "status":state_unknown["status"],
        "transitions":stages_unknown,
        "sandbox":state_unknown["sandbox"]
    }
)

print("\n=== BLOCK: ARGUMENT LIMIT ===")
state_limit=workflow.run(
    event,
    "architecture",
    tool_call={"name":"calculator","arguments":{"a":1000001,"b":1,"op":"+"}}
)
evidence["runs"].append(state_limit)
stages_limit=[x["stage"] for x in state_limit["transitions"]]
add("sandbox_blocks_argument_limit",
    state_limit["status"]=="denied"
    and "tool" not in stages_limit
    and "agent" not in stages_limit
    and state_limit["sandbox"]
    and state_limit["sandbox"][0]["reason"]=="number_limit",
    {
        "status":state_limit["status"],
        "transitions":stages_limit,
        "sandbox":state_limit["sandbox"]
    }
)

print("\n=== POLICY BEFORE SANDBOX ===")
ib=assembler.competency("ib_demo")
ib_event=api.normalize({
    "type":"ib-knowledge",
    "content":ib.tests[0]["prompt"],
    "metadata":{"stage":13}
})
state_policy=workflow.run(
    ib_event,
    "ib-knowledge",
    tool_call={"name":"calculator","arguments":{"a":1,"b":1,"op":"+"}}
)
evidence["runs"].append(state_policy)
stages_policy=[x["stage"] for x in state_policy["transitions"]]
add("policy_precedes_sandbox",
    state_policy["status"]=="denied"
    and "policy_tool" in stages_policy
    and "sandbox" not in stages_policy
    and "tool" not in stages_policy,
    {
        "status":state_policy["status"],
        "transitions":stages_policy,
        "policy":state_policy["policy"]
    }
)

print("\n=== SANDBOX AUDIT ===")
rows=[]
if audit_path.exists():
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
sandbox_rows=[x for x in rows if x["stage"]=="sandbox"]
blocked_rows=[x for x in sandbox_rows if x["status"]=="blocked"]
add("sandbox_decisions_audited",len(sandbox_rows)>=3 and len(blocked_rows)>=2,{
    "audit_path":str(audit_path),
    "sandbox_rows":len(sandbox_rows),
    "blocked_rows":len(blocked_rows)
})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage13_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("AUDIT:",audit_path)
raise SystemExit(0 if release else 1)
