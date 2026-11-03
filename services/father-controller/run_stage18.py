import json
import subprocess
from pathlib import Path

BASE=Path(__file__).resolve().parent
local_anchor_path=BASE/"evidence/stage17_anchor.json"
committed_anchor_path=BASE/"config/anchors/stage17_anchor_committed.json"
evidence_path=BASE/"evidence/stage18_evidence.json"

evidence={
    "stage":"FATHER Chassis v2.7 / Stage 18",
    "goal":"prove local trust-chain anchor matches a GitHub-committed external anchor",
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== LOAD LOCAL + GITHUB-COMMITTED ANCHORS ===")
local=json.loads(local_anchor_path.read_text(encoding="utf-8"))
committed=json.loads(committed_anchor_path.read_text(encoding="utf-8"))

add("local_anchor_present",bool(local),local)
add("committed_anchor_present",bool(committed),committed)
add("local_matches_committed",local==committed,{
    "local":local,
    "committed":committed
})

print("\n=== VERIFY GIT COMMIT ANCHOR ===")
repo_root=BASE.parent.parent
try:
    proc=subprocess.run(
        ["git","log","origin/main","-1","--format=%H","--",
         "services/father-controller/config/anchors/stage17_anchor_committed.json"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=10,
        check=True
    )
    actual_commit=proc.stdout.strip()
except Exception as e:
    actual_commit=""
    add("git_anchor_commit_resolved",False,{"error":str(e)})
else:
    add("git_anchor_commit_resolved",bool(actual_commit),{"commit":actual_commit})

expected_commit="c5f69c6abc739d8187c3ed293fed7d75a4b28d2a"
add("git_anchor_commit_matches_expected",actual_commit==expected_commit,{
    "expected":expected_commit,
    "actual":actual_commit
})

print("\n=== NEGATIVE CONTROL: LOCAL ANCHOR MODIFICATION ===")
tampered=dict(local)
tampered["ledger_entries"]=tampered.get("ledger_entries",0)+1
add("github_anchor_detects_local_change",tampered!=committed,{
    "tampered":tampered,
    "committed":committed
})

print("\n=== NEGATIVE CONTROL: LOCAL ROLLBACK ===")
rolled=dict(local)
rolled["ledger_entries"]=2
rolled["ledger_head_hash"]="3b8d795b6475a7f2ef875ae8f7df099660dacd24220478a05ebe0c4c195ac49a"
add("github_anchor_detects_local_rollback",rolled!=committed,{
    "rolled_back":rolled,
    "committed":committed
})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
evidence["github_anchor_commit"]=actual_commit

evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",evidence_path)
print("GITHUB ANCHOR COMMIT:",actual_commit)
raise SystemExit(0 if release else 1)
