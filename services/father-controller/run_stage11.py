import json
from pathlib import Path

from father.core.agent_zoo import AgentZoo
from father.core.agent_router import AgentRouter
from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter, FileInputAdapter
from father.core.scoring import score_response
from father.core.workflow import WorkflowOrchestrator

BASE=Path(__file__).resolve().parent
zoo=AgentZoo(BASE/"config/agents")
router=AgentRouter(BASE/"config/agent_routes.json",zoo)
assembler=AgentAssembler(BASE)
api=ApiInputAdapter()
file_in=FileInputAdapter()
audit_path=BASE/"evidence/stage11_audit.jsonl"
if audit_path.exists():
    audit_path.unlink()
workflow=WorkflowOrchestrator(router,assembler,audit_path)

evidence={
    "stage":"FATHER Chassis v2.0 / Stage 11",
    "goal":"prove event -> router -> agent/tool -> state -> audit -> result workflow",
    "checks":[],
    "runs":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== WORKFLOW 1: API -> IB AGENT ===")
ib=assembler.competency("ib_demo")
ib_test=ib.tests[0]
event1=api.normalize({
    "type":"ib-knowledge",
    "content":ib_test["prompt"],
    "metadata":{"workflow":"stage11-api-ib"}
})
state1=workflow.run(event1,"ib-knowledge")
result1=state1["result"]
quality1=score_response(result1["content"],ib_test["rubric"])
evidence["runs"].append(state1)

add("workflow_api_completed",state1["status"]=="completed",{
    "run_id":state1["run_id"],
    "agent_id":state1["agent_id"],
    "brain_id":state1["brain_id"],
    "knowledge_hits":state1["knowledge_hits"]
})
add("workflow_api_routed_to_ib",state1["agent_id"]=="father-ib-agent",state1["route"])
add("workflow_api_quality",quality1["passed"],quality1)

print("\n=== WORKFLOW 2: FILE -> GENERAL + TOOL ===")
generic=assembler.competency("generic")
generic_test=generic.tests[1]
input_path=BASE/"data/stage11_input.txt"
input_path.parent.mkdir(parents=True,exist_ok=True)
input_path.write_text(generic_test["prompt"],encoding="utf-8")
event2=file_in.normalize(input_path)
event2.type="architecture"
event2.metadata["workflow"]="stage11-file-tool"
state2=workflow.run(
    event2,
    "architecture",
    tool_call={"name":"calculator","arguments":{"a":6,"b":7,"op":"*"}}
)
result2=state2["result"]
quality2=score_response(result2["content"],generic_test["rubric"])
evidence["runs"].append(state2)

add("workflow_file_completed",state2["status"]=="completed",{
    "run_id":state2["run_id"],
    "agent_id":state2["agent_id"],
    "event_source":state2["event_source"]
})
add("workflow_tool_executed",state2["tool"] is not None and state2["tool"]["ok"] and state2["tool"]["result"]==42,state2["tool"])
add("workflow_file_quality",quality2["passed"],quality2)

print("\n=== STATE TRANSITIONS ===")
expected_api=["event","route","assemble","agent","complete"]
actual_api=[x["stage"] for x in state1["transitions"]]
expected_tool=["event","route","assemble","tool","agent","complete"]
actual_tool=[x["stage"] for x in state2["transitions"]]

add("state_machine_api",actual_api==expected_api,{
    "expected":expected_api,
    "actual":actual_api
})
add("state_machine_tool",actual_tool==expected_tool,{
    "expected":expected_tool,
    "actual":actual_tool
})

print("\n=== AUDIT TRACE ===")
audit_rows=[]
if audit_path.exists():
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            audit_rows.append(json.loads(line))

run_ids={x["run_id"] for x in audit_rows}
audit_ok=(
    state1["run_id"] in run_ids
    and state2["run_id"] in run_ids
    and len(audit_rows)==len(state1["transitions"])+len(state2["transitions"])
)
add("audit_trace_complete",audit_ok,{
    "audit_path":str(audit_path),
    "rows":len(audit_rows),
    "run_ids":sorted(run_ids)
})

print("\n=== FAILURE PATH: BAD TOOL ===")
bad_event=api.normalize({
    "type":"architecture",
    "content":"test failure path"
})
bad_state=workflow.run(
    bad_event,
    "architecture",
    tool_call={"name":"tool-that-does-not-exist","arguments":{}}
)
evidence["runs"].append(bad_state)
bad_stages=[x["stage"] for x in bad_state["transitions"]]
failure_ok=(
    bad_state["status"]=="failed"
    and bad_state["tool"] is not None
    and bad_state["tool"]["ok"] is False
    and "agent" not in bad_stages
)
add("workflow_blocks_after_tool_failure",failure_ok,{
    "status":bad_state["status"],
    "tool":bad_state["tool"],
    "transitions":bad_stages
})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage11_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("AUDIT:",audit_path)
raise SystemExit(0 if release else 1)
