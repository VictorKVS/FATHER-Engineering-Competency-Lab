import copy
import json
from pathlib import Path

from father.core.checkpoint import LedgerCheckpoint
from father.core.evidence_ledger import EvidenceLedger
from father.core.external_anchor import ExternalAnchor

BASE=Path(__file__).resolve().parent
ledger_path=BASE/"evidence/stage15_ledger.jsonl"
checkpoint_path=BASE/"evidence/stage16_checkpoint.json"
anchor_path=BASE/"evidence/stage17_anchor.json"
evidence_path=BASE/"evidence/stage17_evidence.json"

evidence={
    "stage":"FATHER Chassis v2.6 / Stage 17",
    "goal":"prove external anchor artifact for ledger/checkpoint state",
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== LOAD TRUST CHAIN ===")
ledger=EvidenceLedger(ledger_path)
ledger_status=ledger.verify()
add("ledger_valid",ledger_status["ok"],ledger_status)

checkpoint=LedgerCheckpoint(
    checkpoint_path,
    key="FATHER_STAGE16_DEMO_CHECKPOINT_KEY"
)
cp=checkpoint.load()
cp_verify=checkpoint.verify(ledger_status,cp)
add("checkpoint_valid",cp_verify["ok"],cp_verify)

print("\n=== CREATE EXTERNAL ANCHOR ARTIFACT ===")
anchor=ExternalAnchor(anchor_path)
payload=anchor.create(ledger_status,checkpoint_path)
verify=anchor.verify(ledger_status,checkpoint_path)
add("anchor_valid",verify["ok"],verify)

print("\n=== NEGATIVE CONTROL: CHECKPOINT FILE CHANGED ===")
original_checkpoint=checkpoint_path.read_text(encoding="utf-8")
tampered=copy.deepcopy(cp)
tampered["payload"]["head_hash"]="stage17-tampered"
checkpoint_path.write_text(json.dumps(tampered,ensure_ascii=False,indent=2),encoding="utf-8")
checkpoint_changed=anchor.verify(ledger_status,checkpoint_path)
add("anchor_detects_checkpoint_change",checkpoint_changed["ok"] is False,checkpoint_changed)
checkpoint_path.write_text(original_checkpoint,encoding="utf-8")

print("\n=== NEGATIVE CONTROL: LEDGER HEAD CHANGED ===")
original_ledger=ledger_path.read_text(encoding="utf-8")
rows=ledger.rows()
rolled=rows[:-1]
ledger_path.write_text(
    "\n".join(json.dumps(x,ensure_ascii=False) for x in rolled)+"\n",
    encoding="utf-8"
)
rolled_status=ledger.verify()
ledger_changed=anchor.verify(rolled_status,checkpoint_path)
add("anchor_detects_ledger_change",ledger_changed["ok"] is False,ledger_changed)
ledger_path.write_text(original_ledger,encoding="utf-8")

restored=anchor.verify(ledger.verify(),checkpoint_path)
add("anchor_restored_valid",restored["ok"],restored)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
evidence["anchor"]=payload

evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",evidence_path)
print("ANCHOR:",anchor_path)
raise SystemExit(0 if release else 1)
