param(
    [Parameter(Mandatory=$true)]
    [string]$SnapshotSha256,

    [Parameter(Mandatory=$false)]
    [string]$Approver = $env:USERNAME
)

$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

$SnapshotPath = Join-Path $Repo "factory\evidence\FUA-001-HUMAN-ACCEPTANCE-SNAPSHOT.json"
if (-not (Test-Path $SnapshotPath)) {
    throw "human-acceptance snapshot file not found"
}

$Snapshot = Get-Content $SnapshotPath -Raw | ConvertFrom-Json
$CurrentCommit = (git rev-parse HEAD).Trim()

if ($Snapshot.snapshot_sha256 -ne $SnapshotSha256) {
    throw "snapshot hash mismatch"
}

if ($Snapshot.commit_sha -ne $CurrentCommit) {
    throw "repository HEAD differs from accepted snapshot commit"
}

$AcceptancePath = Join-Path $Repo "factory\evidence\FUA-001-HUMAN-ACCEPTANCE.json"
$TempPy = Join-Path $env:TEMP "fua-human-acceptance-apply.py"

@'
import json
import sys
import time
from pathlib import Path

from father_fua.human_acceptance import HumanAcceptance, verify_human_acceptance

snapshot_path=Path(sys.argv[1])
acceptance_path=Path(sys.argv[2])
provided_hash=sys.argv[3]
approver=sys.argv[4]

snapshot=json.loads(snapshot_path.read_text(encoding="utf-8"))

if snapshot["snapshot_sha256"] != provided_hash:
    raise SystemExit("snapshot hash mismatch")

acceptance=HumanAcceptance(
    acceptance_id=f"HA-{int(time.time())}",
    snapshot_sha256=provided_hash,
    requester="FATHER_FACTORY",
    approver=approver,
    decision="ACCEPT",
    expires_at=time.time()+86400,
)

if not verify_human_acceptance(
    acceptance,
    current_snapshot_sha256=provided_hash,
):
    raise SystemExit("human acceptance verification failed")

payload={
    "schema":"father.human_acceptance.v1",
    "acceptance_id":acceptance.acceptance_id,
    "snapshot_sha256":acceptance.snapshot_sha256,
    "commit_sha":snapshot["commit_sha"],
    "requester":acceptance.requester,
    "approver":acceptance.approver,
    "decision":acceptance.decision,
    "expires_at":acceptance.expires_at,
    "verified":True,
}

acceptance_path.write_text(json.dumps(payload,indent=2),encoding="utf-8")

print("HUMAN ACCEPTANCE : PASS")
print("ACCEPTANCE ID    :",payload["acceptance_id"])
print("APPROVER         :",payload["approver"])
print("COMMIT SHA       :",payload["commit_sha"])
print("SNAPSHOT SHA256  :",payload["snapshot_sha256"])
print("ACCEPTANCE FILE  :",str(acceptance_path))
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy $SnapshotPath $AcceptancePath $SnapshotSha256 $Approver
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) {
    throw "human acceptance failed with exit code $Code"
}
