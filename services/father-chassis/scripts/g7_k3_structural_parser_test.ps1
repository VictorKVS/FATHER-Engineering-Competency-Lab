param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_k3_structural_parser_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_K3_STRUCTURAL_PARSER"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 approved_source_parsed=$false
 deterministic_document_hash=$false
 structure_order_preserved=$false
 locators_preserved=$false
 hold_rejected=$false
 forged_provenance_rejected=$false
 content_hash_mismatch_rejected=$false
 invalid_utf8_rejected=$false
 unsupported_media_rejected=$false
 source_binding_preserved=$false
 no_raw_source_git_evidence=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[G7 K3] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[G7 K3] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:G7_K3_ARTIFACT=$artifactPath

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
)
from father.knowledge_factory.structural_parser import (
    DeterministicTextStructuralParser,
    StructuralParseRequest,
)

artifact_path=Path(os.environ["G7_K3_ARTIFACT"])
content=b"# TITLE\n\nFirst paragraph line one.\nline two.\n\nSECTION TWO\n\nSecond paragraph."

service=SourceIntakeService(InMemorySourceIntakeRegistry())
intake=service.intake(SourceCandidate(
    source_id="SRC-K3",
    source_class="reference",
    title="K3 Source",
    locator="file:///knowledge/k3.md",
    version="1.0",
    content_bytes=content,
    declared_access="PUBLIC",
    declared_rights="DECLARED_PUBLIC",
)).record
policy=SourceUsePolicy(
    policy_id="POL-K3-1",
    version="1.0.0",
    allowed_rights=frozenset({"DECLARED_PUBLIC"}),
    denied_rights=frozenset(),
    allowed_access=frozenset({"PUBLIC"}),
    required_evidence_types=frozenset({"rights_basis"}),
)
evidence=(PolicyEvidence(
    evidence_id="EV-K3-1",
    evidence_type="rights_basis",
    authority="owner",
    locator="evidence://k3/1",
    evidence_hash="a"*64,
),)
decision,provenance=LegalAccessEvaluator().evaluate(
    intake=intake,policy=policy,evidence=evidence
)
assert decision.status=="APPROVED"

parser=DeterministicTextStructuralParser()
request=StructuralParseRequest(
    intake=intake,
    decision=decision,
    provenance=provenance,
    content_bytes=content,
    media_type="text/markdown",
)
first=parser.parse(request)
second=parser.parse(request)
assert first.status=="PARSED"
assert first.document is not None
assert first.document.document_hash==second.document.document_hash
assert [u.unit_type for u in first.document.units]==["heading","paragraph","heading","paragraph"]
assert [u.ordinal for u in first.document.units]==[0,1,2,3]
assert first.document.units[0].locator=="line:1-1"
assert first.document.units[1].locator=="line:3-4"
for unit in first.document.units:
    assert unit.source_id==intake.source_id
    assert unit.source_content_hash==intake.content_hash

hold=parser.parse(replace(request,decision=replace(decision,status="HOLD")))
assert hold.status=="REJECTED"

forged=parser.parse(replace(
    request,
    provenance=replace(provenance,source_content_hash="b"*64),
))
assert forged.status=="REJECTED"
assert any("provenance content_hash mismatch" in x for x in forged.diagnostics)

mismatch=parser.parse(replace(request,content_bytes=b"different"))
assert mismatch.status=="REJECTED"

invalid_content=b"\xff\xfe"
invalid_intake=service.intake(SourceCandidate(
    source_id="SRC-K3-INVALID",
    source_class="reference",
    title="Invalid UTF8",
    locator="file:///knowledge/invalid.txt",
    version="1.0",
    content_bytes=invalid_content,
    declared_access="PUBLIC",
    declared_rights="DECLARED_PUBLIC",
)).record
invalid_decision,invalid_provenance=LegalAccessEvaluator().evaluate(
    intake=invalid_intake,policy=policy,evidence=evidence
)
invalid=parser.parse(StructuralParseRequest(
    intake=invalid_intake,
    decision=invalid_decision,
    provenance=invalid_provenance,
    content_bytes=invalid_content,
    media_type="text/plain",
))
assert invalid.status=="REJECTED"
assert any("invalid UTF-8" in x for x in invalid.diagnostics)

unsupported=parser.parse(replace(request,media_type="application/pdf"))
assert unsupported.status=="REJECTED"

payload={
 "approved_source_parsed":True,
 "deterministic_document_hash":True,
 "structure_order_preserved":True,
 "locators_preserved":True,
 "hold_rejected":True,
 "forged_provenance_rejected":True,
 "content_hash_mismatch_rejected":True,
 "invalid_utf8_rejected":True,
 "unsupported_media_rejected":True,
 "source_binding_preserved":True,
 "no_raw_source_git_evidence":True,
 "source_id":intake.source_id,
 "source_hash":intake.content_hash,
 "document_id":first.document.document_id,
 "document_hash":first.document.document_hash,
 "unit_count":len(first.document.units),
 "parser_id":first.document.parser_id,
 "parser_version":first.document.parser_version,
 "completed_at_utc":datetime.now(timezone.utc).isoformat(),
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Structural parser qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @("approved_source_parsed","deterministic_document_hash","structure_order_preserved","locators_preserved","hold_rejected","forged_provenance_rejected","content_hash_mismatch_rejected","invalid_utf8_rejected","unsupported_media_rejected","source_binding_preserved","no_raw_source_git_evidence")){
    $result[$name]=[bool]$runtime.$name
  }
  $result.passed=$result.toolchain_ready -and $result.regression -and $result.approved_source_parsed -and $result.deterministic_document_hash -and $result.structure_order_preserved -and $result.locators_preserved -and $result.hold_rejected -and $result.forged_provenance_rejected -and $result.content_hash_mismatch_rejected -and $result.invalid_utf8_rejected -and $result.unsupported_media_rejected -and $result.source_binding_preserved -and $result.no_raw_source_git_evidence
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 K3 STRUCTURAL PARSER: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 K3 STRUCTURAL PARSER: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
