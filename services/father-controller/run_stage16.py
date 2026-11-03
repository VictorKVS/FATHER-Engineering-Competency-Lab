import copy
import json
from pathlib import Path

from father.core.checkpoint import LedgerCheckpoint
from father.core.evidence_ledger import EvidenceLedger

BASE=Path(__file__).resolve().parent
ledger_path=BASE/"evidence/stage15_ledger.jsonl"
checkpoint_path=BASE/"evidence/stage16_checkpoint.json"
evidence_path=BASE/"evidence/stage16_evidence.json"

evidence={
    "stage":"FATHER Chassis v2.5 / Stage 16",
    "goal":"prove authenticated checkpoint for ledger head and rollback detection",
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== LOAD LEDGER ===")
ledger=EvidenceLedger(ledger_path)
status=ledger.verify()
add("ledger_available",status["ok"] and status["entries"]>=3,status)

print("\n=== CREATE AUTHENTICATED CHECKPOINT ===")
checkpoint=LedgerCheckpoint(
    checkpoint_path,
    key="FATHER_STAGE16_DEMO_CHECKPOINT_KEY"
)
cp=checkpoint.create(status)
verify=checkpoint.verify(status,cp)
add("checkpoint_valid",verify["ok"],verify)

print("\n=== NEGATIVE CONTROL: CHECKPOINT MODIFICATION ===")
tampered=copy.deepcopy(cp)
tampered["payload"]["head_hash"]="tampered-head"
tampered_check=checkpoint.verify(status,tampered)
add("checkpoint_detects_modification",
    tampered_check["ok"] is False and tampered_check["mac_ok"] is False,
    tampered_check
)

print("\n=== NEGATIVE CONTROL: WRONG KEY ===")
wrong=LedgerCheckpoint(
    checkpoint_path,
    key="WRONG_STAGE16_KEY"
)
wrong_key_check=wrong.verify(status,cp)
add("checkpoint_detects_wrong_key",
    wrong_key_check["ok"] is False and wrong_key_check["mac_ok"] is False,
    wrong_key_check
)

print("\n=== NEGATIVE CONTROL: LEDGER ROLLBACK ===")
rows=ledger.rows()
original_text=ledger_path.read_text(encoding="utf-8")
rolled_back=rows[:-1]
ledger_path.write_text(
    "\n".join(json.dumps(x,ensure_ascii=False) for x in rolled_back)+"\n",
    encoding="utf-8"
)
rollback_status=ledger.verify()
rollback_check=checkpoint.verify(rollback_status,cp)
add("checkpoint_detects_rollback",
    rollback_check["ok"] is False and rollback_check["ledger_match"] is False,
    rollback_check
)

ledger_path.write_text(original_text,encoding="utf-8")
restored_status=ledger.verify()
restored_check=checkpoint.verify(restored_status,cp)
add("checkpoint_restored_valid",restored_check["ok"],restored_check)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
evidence["checkpoint"]=cp

evidence_path.parent.mkdir(parents=True,exist_ok=True)
evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",evidence_path)
print("CHECKPOINT:",checkpoint_path)
raise SystemExit(0 if release else 1)
