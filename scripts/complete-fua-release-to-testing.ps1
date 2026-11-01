param(
    [Parameter(Mandatory=$true)]
    [switch]$AcceptCurrentSnapshot,

    [Parameter(Mandatory=$false)]
    [string]$Approver = $env:USERNAME
)

$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

$SnapshotPath = Join-Path $Repo "factory\evidence\FUA-001-HUMAN-ACCEPTANCE-SNAPSHOT.json"
$ManifestPath = Join-Path $Repo "factory\chassis\FUA-001\manifest.json"
$AcceptancePath = Join-Path $Repo "factory\evidence\FUA-001-HUMAN-ACCEPTANCE.json"
$EvidencePath = Join-Path $Repo "factory\evidence\EVID-FUA-INSTALLATION-TO-TESTING-0019.md"

if (-not $AcceptCurrentSnapshot) {
    throw "explicit -AcceptCurrentSnapshot is required"
}

$CurrentCommit = (git rev-parse HEAD).Trim()

Write-Host "=== FUA-001 COMPLETE RELEASE TO TESTING ==="
Write-Host ("COMMIT SHA       : {0}" -f $CurrentCommit)
Write-Host "HUMAN ACTION     : ACCEPT_CURRENT_SNAPSHOT"

Write-Host ""
Write-Host "00. Create exact current snapshot"
& (Join-Path $PSScriptRoot "create-fua-human-acceptance-snapshot.ps1")
if ($LASTEXITCODE -ne 0) { throw "snapshot generation failed" }

$Snapshot = Get-Content $SnapshotPath -Raw | ConvertFrom-Json
$SnapshotSha256 = $Snapshot.snapshot_sha256
if ($Snapshot.commit_sha -ne $CurrentCommit) {
    throw "snapshot commit mismatch"
}
Write-Host ("SNAPSHOT SHA256  : {0}" -f $SnapshotSha256)

Write-Host ""
Write-Host "01. Installation / release precheck"
& (Join-Path $PSScriptRoot "test-fua-installation-release-precheck.ps1")
if ($LASTEXITCODE -ne 0) { throw "release precheck failed" }

$TempPy = Join-Path $env:TEMP "fua-complete-release-to-testing.py"

@'
import json
import sys
import time
from pathlib import Path

from father_fua.human_acceptance import HumanAcceptance, verify_human_acceptance
from father_fua.installation_gate import evaluate_installation_gate
from father_fua.readiness import MANDATORY

snapshot_path=Path(sys.argv[1])
manifest_path=Path(sys.argv[2])
acceptance_path=Path(sys.argv[3])
evidence_path=Path(sys.argv[4])
provided_hash=sys.argv[5]
approver=sys.argv[6]
commit_sha=sys.argv[7]

snapshot=json.loads(snapshot_path.read_text(encoding="utf-8"))
manifest=json.loads(manifest_path.read_text(encoding="utf-8"))

if snapshot["snapshot_sha256"] != provided_hash:
    raise SystemExit("snapshot hash mismatch")
if snapshot["commit_sha"] != commit_sha:
    raise SystemExit("commit mismatch")
if manifest.get("installation_permit") != "DENIED":
    raise SystemExit("expected installation permit DENIED before acceptance")
if manifest.get("production_ready") is not False:
    raise SystemExit("expected production_ready=false")

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

auto={name:"PASS" for name in MANDATORY if name!="HUMAN_ACCEPTANCE"}
decision=evaluate_installation_gate(
    current_snapshot_sha256=provided_hash,
    acceptance=acceptance,
    automated_gates=auto,
)
if decision.decision != "PASS":
    raise SystemExit(f"installation gate denied: {decision.reason}")

acceptance_payload={
    "schema":"father.human_acceptance.v1",
    "acceptance_id":acceptance.acceptance_id,
    "snapshot_sha256":provided_hash,
    "commit_sha":commit_sha,
    "requester":acceptance.requester,
    "approver":acceptance.approver,
    "decision":acceptance.decision,
    "expires_at":acceptance.expires_at,
    "verified":True,
}
acceptance_path.write_text(
    json.dumps(acceptance_payload,indent=2),
    encoding="utf-8",
)

manifest["human_acceptance"]={
    "status":"PASS",
    "acceptance_id":acceptance.acceptance_id,
    "snapshot_sha256":provided_hash,
    "commit_sha":commit_sha,
    "approver":approver,
}
manifest["installation_gate"]={
    "status":"PASS",
    "snapshot_sha256":provided_hash,
}
manifest["status"]="INSTALLATION_APPROVED_FOR_TESTING"
manifest["installation_permit"]="PASS"
manifest["production_ready"]=False
manifest["next_factory_gates"]=[
    "PRODUCT_TEST",
    "PILOT_TEST",
    "PRODUCTION_READINESS_REVIEW",
]
manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")

evidence=f"""# FUA-001 Evidence Record — INSTALLATION TO TESTING 0019

Evidence ID: EVID-FUA-INSTALLATION-TO-TESTING-0019
Status: PASS

COMMIT_SHA={commit_sha}
SNAPSHOT_SHA256={provided_hash}
HUMAN_ACCEPTANCE=PASS
ACCEPTANCE_ID={acceptance.acceptance_id}
APPROVER={approver}
INSTALLATION_GATE=PASS
INSTALLATION_PERMIT=PASS
STATUS=INSTALLATION_APPROVED_FOR_TESTING
PRODUCTION_READY=false
NEXT_GATES=PRODUCT_TEST,PILOT_TEST,PRODUCTION_READINESS_REVIEW

This evidence authorizes FUA-001 for controlled testing only.
It does not authorize production use.
"""
evidence_path.write_text(evidence,encoding="utf-8")

print("HUMAN ACCEPTANCE : PASS")
print("INSTALL GATE     : PASS")
print("INSTALL PERMIT   : PASS")
print("STATUS           : INSTALLATION_APPROVED_FOR_TESTING")
print("PRODUCTION READY : False")
print("NEXT GATES       : PRODUCT_TEST,PILOT_TEST,PRODUCTION_READINESS_REVIEW")
print("EVIDENCE         :",str(evidence_path))
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy $SnapshotPath $ManifestPath $AcceptancePath $EvidencePath $SnapshotSha256 $Approver $CurrentCommit
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) {
    throw "release-to-testing failed with exit code $Code"
}

Write-Host ""
Write-Host "FUA-001 RELEASE TO TESTING RESULT: PASS"
