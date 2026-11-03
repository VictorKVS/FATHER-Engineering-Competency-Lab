import copy
import json
from pathlib import Path

from father.core.agent_zoo import AgentZoo
from father.core.agent_router import AgentRouter
from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter
from father.core.policy import PolicyGate
from father.core.provenance import build_bundle, verify_bundle
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

audit_path=BASE/"evidence/stage14_audit.jsonl"
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
    "stage":"FATHER Chassis v2.3 / Stage 14",
    "goal":"prove reconstructable evidence/provenance and integrity verification",
    "checks":[],
    "bundle":None
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== EXECUTE TRACEABLE RUN ===")
generic=assembler.competency("generic")
test=generic.tests[0]
event=api.normalize({
    "type":"architecture",
    "content":test["prompt"],
    "metadata":{"stage":14,"evidence":"provenance"}
})
state=workflow.run(
    event,
    "architecture",
    tool_call={"name":"calculator","arguments":{"a":2,"b":3,"op":"+"}}
)
quality=score_response(state["result"]["content"],test["rubric"]) if state.get("result") else {"passed":False}
add("traceable_run_completed",state["status"]=="completed" and quality["passed"],{
    "run_id":state["run_id"],
    "status":state["status"],
    "quality":quality
})

rows=[]
for line in audit_path.read_text(encoding="utf-8").splitlines():
    if line.strip():
        row=json.loads(line)
        if row.get("run_id")==state["run_id"]:
            rows.append(row)

print("\n=== BUILD PROVENANCE BUNDLE ===")
bundle=build_bundle(state,rows)
evidence["bundle"]=bundle
verify=verify_bundle(bundle)
add("provenance_bundle_valid",verify["ok"],verify)

add("provenance_has_route",bool(bundle.get("route") and bundle["route"].get("agent_id")),bundle.get("route"))
add("provenance_has_policy",len(bundle.get("policy",[]))>=2,{"policy":bundle.get("policy")})
add("provenance_has_sandbox",len(bundle.get("sandbox",[]))>=1,{"sandbox":bundle.get("sandbox")})
add("provenance_has_tool",bool(bundle.get("tool") and bundle["tool"].get("ok")),bundle.get("tool"))
add("provenance_has_knowledge_sources",bundle["knowledge"]["hits"]>0 and bool(bundle["knowledge"]["sources"]),bundle["knowledge"])
add("provenance_has_result",bool(bundle.get("result") and bundle["result"].get("ok")),{
    "result_ok":bundle["result"].get("ok"),
    "model":bundle["result"].get("model"),
    "provider":bundle["result"].get("provider")
})

print("\n=== NEGATIVE CONTROL: RESULT MODIFICATION ===")
modified=copy.deepcopy(bundle)
modified["result"]["content"]="modified-result"
modified_check=verify_bundle(modified)
add("integrity_detects_result_change",modified_check["ok"] is False and modified_check["digests_ok"] is False,modified_check)

print("\n=== NEGATIVE CONTROL: INCOMPLETE TRACE ===")
incomplete=copy.deepcopy(bundle)
incomplete["audit_rows"]=[row for row in incomplete["audit_rows"] if row.get("stage")!="route"]
incomplete["digests"]["audit_rows"]=__import__("father.core.provenance",fromlist=["digest"]).digest(incomplete["audit_rows"])
incomplete["bundle_digest"]=__import__("father.core.provenance",fromlist=["digest"]).digest(incomplete["digests"])
incomplete_check=verify_bundle(incomplete)
add("integrity_detects_incomplete_trace",incomplete_check["ok"] is False and incomplete_check["trace_ok"] is False,incomplete_check)

bundle_path=BASE/"evidence/stage14_provenance.json"
bundle_path.write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding="utf-8")

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
out=BASE/"evidence/stage14_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("PROVENANCE:",bundle_path)
print("AUDIT:",audit_path)
raise SystemExit(0 if release else 1)
