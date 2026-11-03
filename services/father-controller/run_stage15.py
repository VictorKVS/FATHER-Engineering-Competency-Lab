import copy
import json
from pathlib import Path

from father.core.agent_zoo import AgentZoo
from father.core.agent_router import AgentRouter
from father.core.assembler import AgentAssembler
from father.core.evidence_ledger import EvidenceLedger
from father.core.io import ApiInputAdapter
from father.core.policy import PolicyGate
from father.core.provenance import build_bundle, verify_bundle
from father.core.sandbox import ExecutionSandbox
from father.core.workflow import WorkflowOrchestrator

BASE=Path(__file__).resolve().parent
zoo=AgentZoo(BASE/"config/agents")
router=AgentRouter(BASE/"config/agent_routes.json",zoo)
assembler=AgentAssembler(BASE)
policy=PolicyGate(BASE/"config/policies.json")
sandbox=ExecutionSandbox(timeout_sec=2,max_text_chars=2000,max_abs_number=1000000)
api=ApiInputAdapter()

audit_path=BASE/"evidence/stage15_audit.jsonl"
ledger_path=BASE/"evidence/stage15_ledger.jsonl"
if audit_path.exists():
    audit_path.unlink()
if ledger_path.exists():
    ledger_path.unlink()

workflow=WorkflowOrchestrator(
    router,
    assembler,
    audit_path,
    policy_gate=policy,
    sandbox=sandbox
)
ledger=EvidenceLedger(ledger_path)

evidence={
    "stage":"FATHER Chassis v2.4 / Stage 15",
    "goal":"prove append-only evidence ledger with chained integrity",
    "checks":[],
    "entries":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

def audit_for(run_id):
    rows=[]
    if audit_path.exists():
        for line in audit_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row=json.loads(line)
                if row.get("run_id")==run_id:
                    rows.append(row)
    return rows

print("=== APPEND THREE PROVENANCE ENTRIES ===")
cases=[
    ("architecture","Что такое Brain Slot в FATHER?",{"name":"calculator","arguments":{"a":2,"b":2,"op":"+"}}),
    ("architecture","Что такое Knowledge Slot в FATHER?",None),
    ("ib-knowledge","Перечисли нормативные документы в подключенной БЗ.",None)
]

for task_type,prompt,tool_call in cases:
    event=api.normalize({"type":task_type,"content":prompt,"metadata":{"stage":15}})
    state=workflow.run(event,task_type,tool_call=tool_call)
    rows=audit_for(state["run_id"])
    bundle=build_bundle(state,rows)
    bundle_check=verify_bundle(bundle)
    entry=ledger.append(bundle)
    evidence["entries"].append(entry)
    add("bundle_"+str(entry["seq"]),state["status"]=="completed" and bundle_check["ok"],{
        "run_id":state["run_id"],
        "bundle_ok":bundle_check["ok"],
        "entry":entry
    })

print("\n=== VERIFY CHAIN ===")
chain=ledger.verify()
add("ledger_chain_valid",chain["ok"] and chain["entries"]==3,chain)

rows=ledger.rows()
add("ledger_sequence", [x["seq"] for x in rows]==[1,2,3],{
    "sequence":[x["seq"] for x in rows]
})
add("ledger_links",rows[0]["prev_hash"]=="GENESIS"
    and rows[1]["prev_hash"]==rows[0]["entry_hash"]
    and rows[2]["prev_hash"]==rows[1]["entry_hash"],{
        "links":[
            rows[0]["prev_hash"],
            rows[1]["prev_hash"],
            rows[2]["prev_hash"]
        ]
    })

print("\n=== NEGATIVE CONTROL: MODIFY OLD ENTRY ===")
original_text=ledger_path.read_text(encoding="utf-8")
tampered=copy.deepcopy(rows)
tampered[0]["bundle_digest"]="tampered"
ledger_path.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in tampered)+"\n",encoding="utf-8")
modified_check=ledger.verify()
add("ledger_detects_modification",modified_check["ok"] is False and len(modified_check["issues"])>0,modified_check)

print("\n=== NEGATIVE CONTROL: DELETE MIDDLE ENTRY ===")
ledger_path.write_text(original_text,encoding="utf-8")
rows=ledger.rows()
deleted=[rows[0],rows[2]]
ledger_path.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in deleted)+"\n",encoding="utf-8")
delete_check=ledger.verify()
add("ledger_detects_deletion",delete_check["ok"] is False and len(delete_check["issues"])>0,delete_check)

print("\n=== NEGATIVE CONTROL: REORDER ENTRIES ===")
ledger_path.write_text(original_text,encoding="utf-8")
rows=ledger.rows()
reordered=[rows[1],rows[0],rows[2]]
ledger_path.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in reordered)+"\n",encoding="utf-8")
reorder_check=ledger.verify()
add("ledger_detects_reorder",reorder_check["ok"] is False and len(reorder_check["issues"])>0,reorder_check)

ledger_path.write_text(original_text,encoding="utf-8")
final_check=ledger.verify()
add("ledger_restored_valid",final_check["ok"],final_check)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
evidence["final_ledger"]=final_check

out=BASE/"evidence/stage15_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("LEDGER:",ledger_path)
print("AUDIT:",audit_path)
raise SystemExit(0 if release else 1)
