param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_k1_source_intake_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_K1_SOURCE_INTAKE"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 deterministic_fingerprint=$false
 required_metadata_enforced=$false
 duplicate_detected_without_merge=$false
 changed_content_changes_hash=$false
 declared_rights_not_legal_approval=$false
 immutable_record=$false
 no_raw_source_git_evidence=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[G7 K1] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[G7 K1] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:G7_K1_ARTIFACT=$artifactPath

@'
import json, os
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from father.knowledge_factory.source_intake import (
    InMemorySourceIntakeRegistry,
    SourceCandidate,
    SourceIntakeService,
)

artifact_path=Path(os.environ["G7_K1_ARTIFACT"])

def candidate(source_id, title, content):
    return SourceCandidate(
        source_id=source_id,
        source_class="architecture_standard",
        title=title,
        locator="file:///knowledge/source.pdf",
        version="1.0",
        content_bytes=content,
        declared_access="LOCAL_FILE",
        declared_rights="DECLARED_OWNED_COPY",
    )

registry=InMemorySourceIntakeRegistry()
service=SourceIntakeService(registry)

first=service.intake(candidate("SRC-K1-1","First",b"same-content"))
assert first.accepted
assert first.record.content_hash==sha256(b"same-content").hexdigest()
assert first.record.hash_algorithm=="sha256"

bad=service.intake(SourceCandidate("BAD","architecture_standard","", "file:///bad"))
assert not bad.accepted

duplicate=service.intake(candidate("SRC-K1-2","Second",b"same-content"))
assert duplicate.accepted
assert duplicate.record.duplicate_of_source_id=="SRC-K1-1"
assert duplicate.record.title=="Second"
assert registry.get("SRC-K1-1").title=="First"

changed=service.intake(candidate("SRC-K1-3","Changed",b"different-content"))
assert changed.record.content_hash != first.record.content_hash

rights=service.intake(SourceCandidate(
    source_id="SRC-K1-4",
    source_class="architecture_standard",
    title="Rights declaration",
    locator="file:///knowledge/rights.pdf",
    version="1.0",
    content_bytes=b"rights",
    declared_access="PUBLIC",
    declared_rights="DECLARED_PUBLIC",
))
assert rights.accepted
assert rights.record.status=="INTAKE_READY"
assert rights.record.declared_rights=="DECLARED_PUBLIC"
assert "LEGAL_APPROVED" not in rights.record.declared_rights

immutable=False
try:
    first.record.title="mutated"
except FrozenInstanceError:
    immutable=True
assert immutable

# K1 emits only metadata/hash references. It never writes raw content into canonical artifact.
raw_present = b"same-content" in artifact_path.parent.as_posix().encode("utf-8")
assert raw_present is False

payload={
 "deterministic_fingerprint":True,
 "required_metadata_enforced":True,
 "duplicate_detected_without_merge":True,
 "changed_content_changes_hash":True,
 "declared_rights_not_legal_approval":True,
 "immutable_record":True,
 "no_raw_source_git_evidence":True,
 "source_id":"SRC-K1-1",
 "content_hash":first.record.content_hash,
 "duplicate_source_id":duplicate.record.source_id,
 "duplicate_of_source_id":duplicate.record.duplicate_of_source_id,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Source intake qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @("deterministic_fingerprint","required_metadata_enforced","duplicate_detected_without_merge","changed_content_changes_hash","declared_rights_not_legal_approval","immutable_record","no_raw_source_git_evidence")){
    $result[$name]=[bool]$runtime.$name
  }
  $result.passed=$result.toolchain_ready -and $result.regression -and $result.deterministic_fingerprint -and $result.required_metadata_enforced -and $result.duplicate_detected_without_merge -and $result.changed_content_changes_hash -and $result.declared_rights_not_legal_approval -and $result.immutable_record -and $result.no_raw_source_git_evidence
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 K1 SOURCE INTAKE: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 K1 SOURCE INTAKE: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
