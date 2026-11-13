param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_k2_legal_access_provenance_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_K2_LEGAL_ACCESS_PROVENANCE"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 allowed_approved=$false
 denied_rejected=$false
 unknown_held=$false
 missing_evidence_held=$false
 no_hash_held=$false
 provenance_binding_valid=$false
 hash_substitution_detected=$false
 policy_version_preserved=$false
 no_raw_source_git_evidence=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[G7 K2] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[G7 K2] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:G7_K2_ARTIFACT=$artifactPath

@'
import json, os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from father.knowledge_factory.source_intake import (
    InMemorySourceIntakeRegistry,
    SourceCandidate,
    SourceIntakeService,
)
from father.knowledge_factory.legal_provenance import (
    LegalAccessEvaluator,
    PolicyEvidence,
    SourceUsePolicy,
    verify_provenance_binding,
)

artifact_path=Path(os.environ["G7_K2_ARTIFACT"])

def intake(rights="DECLARED_PUBLIC", access="PUBLIC", content=b"source"):
    service=SourceIntakeService(InMemorySourceIntakeRegistry())
    return service.intake(SourceCandidate(
        source_id="SRC-K2",
        source_class="architecture_standard",
        title="Architecture Standard",
        locator="file:///knowledge/source.pdf",
        version="1.0",
        content_bytes=content,
        declared_access=access,
        declared_rights=rights,
    )).record

policy=SourceUsePolicy(
    policy_id="POL-K2-1",
    version="1.0.0",
    allowed_rights=frozenset({"DECLARED_PUBLIC","DECLARED_OWNED_COPY"}),
    denied_rights=frozenset({"DECLARED_DENIED"}),
    allowed_access=frozenset({"PUBLIC","LOCAL_FILE"}),
    required_evidence_types=frozenset({"rights_basis"}),
    allowed_use=("knowledge_processing","retrieval_indexing"),
)
evidence=(PolicyEvidence(
    evidence_id="EV-K2-1",
    evidence_type="rights_basis",
    authority="owner",
    locator="evidence://rights/1",
    evidence_hash="a"*64,
),)

allowed_intake=intake()
decision, provenance=LegalAccessEvaluator().evaluate(
    intake=allowed_intake, policy=policy, evidence=evidence
)
assert decision.status=="APPROVED"
assert decision.allowed_use==("knowledge_processing","retrieval_indexing")
assert verify_provenance_binding(allowed_intake,decision,provenance)==()

denied,_=LegalAccessEvaluator().evaluate(
    intake=intake(rights="DECLARED_DENIED"),policy=policy,evidence=evidence
)
assert denied.status=="REJECTED"

unknown,_=LegalAccessEvaluator().evaluate(
    intake=intake(rights="UNKNOWN"),policy=policy,evidence=evidence
)
assert unknown.status=="HOLD"

missing,_=LegalAccessEvaluator().evaluate(
    intake=intake(),policy=policy,evidence=()
)
assert missing.status=="HOLD"

nohash,_=LegalAccessEvaluator().evaluate(
    intake=intake(content=None),policy=policy,evidence=evidence
)
assert nohash.status=="HOLD"

forged=replace(provenance,source_content_hash="b"*64)
errors=verify_provenance_binding(allowed_intake,decision,forged)
assert "provenance content_hash mismatch" in errors

assert decision.policy_id=="POL-K2-1"
assert decision.policy_version=="1.0.0"

payload={
 "allowed_approved":True,
 "denied_rejected":True,
 "unknown_held":True,
 "missing_evidence_held":True,
 "no_hash_held":True,
 "provenance_binding_valid":True,
 "hash_substitution_detected":True,
 "policy_version_preserved":True,
 "no_raw_source_git_evidence":True,
 "source_id":allowed_intake.source_id,
 "source_hash":allowed_intake.content_hash,
 "decision_id":decision.decision_id,
 "provenance_id":provenance.provenance_id,
 "policy_id":decision.policy_id,
 "policy_version":decision.policy_version,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Legal/Access + Provenance qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @("allowed_approved","denied_rejected","unknown_held","missing_evidence_held","no_hash_held","provenance_binding_valid","hash_substitution_detected","policy_version_preserved","no_raw_source_git_evidence")){
    $result[$name]=[bool]$runtime.$name
  }
  $result.passed=$result.toolchain_ready -and $result.regression -and $result.allowed_approved -and $result.denied_rejected -and $result.unknown_held -and $result.missing_evidence_held -and $result.no_hash_held -and $result.provenance_binding_valid -and $result.hash_substitution_detected -and $result.policy_version_preserved -and $result.no_raw_source_git_evidence
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 K2 LEGAL ACCESS PROVENANCE: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 K2 LEGAL ACCESS PROVENANCE: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
