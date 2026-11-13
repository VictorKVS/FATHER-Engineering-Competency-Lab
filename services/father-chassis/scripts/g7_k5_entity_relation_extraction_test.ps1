param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_k5_entity_relation_extraction_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_K5_ENTITY_RELATION_EXTRACTION"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 valid_chunk_set_extracted=$false
 deterministic_hashes=$false
 entity_evidence_preserved=$false
 relation_evidence_preserved=$false
 duplicate_entities_deduplicated=$false
 unsupported_text_no_invented_relation=$false
 policy_version_changes_identity=$false
 malformed_lineage_rejected=$false
 confidence_bounded=$false
 invalid_policy_rejected=$false
 referential_integrity_preserved=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[G7 K5] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[G7 K5] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:G7_K5_ARTIFACT=$artifactPath

@'
import json, os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from father.knowledge_factory.chunk_normalization import (
    NormalizedChunk,
    NormalizedChunkSet,
)
from father.knowledge_factory.entity_relation import (
    DeterministicRuleExtractor,
    ExtractionPolicy,
)

artifact_path=Path(os.environ["G7_K5_ARTIFACT"])

chunk=NormalizedChunk(
    chunk_id="CHK-K5-1",
    ordinal=0,
    text="Alpha -> Beta. Alpha works with Gamma.",
    chunk_hash="a"*64,
    source_id="SRC-K5",
    document_id="DOC-K5",
    document_hash="b"*64,
    source_unit_ids=("UNIT-K5-1",),
    source_locators=("line:1-1",),
    policy_id="POL-K4",
    policy_version="1.0",
)
chunk_set=NormalizedChunkSet(
    chunk_set_id="CHSET-K5",
    source_id="SRC-K5",
    document_id="DOC-K5",
    document_hash="b"*64,
    normalizer_id="FTH-DETERMINISTIC-NORMALIZER",
    normalizer_version="1.0.0",
    policy_id="POL-K4",
    policy_version="1.0",
    chunks=(chunk,),
    chunk_set_hash="c"*64,
)

extractor=DeterministicRuleExtractor()
policy=ExtractionPolicy("POL-K5","1.0",min_confidence=0.8)
first=extractor.extract(chunk_set,policy)
second=extractor.extract(chunk_set,policy)

assert first.status=="EXTRACTED"
assert first.extraction_set.extraction_set_hash==second.extraction_set.extraction_set_hash
assert [e.entity_hash for e in first.extraction_set.entities]==[e.entity_hash for e in second.extraction_set.entities]
assert [r.relation_hash for r in first.extraction_set.relations]==[r.relation_hash for r in second.extraction_set.relations]

assert all(e.evidence_chunk_ids for e in first.extraction_set.entities)
assert all(r.evidence_chunk_ids for r in first.extraction_set.relations)

entity_ids={e.entity_id for e in first.extraction_set.entities}
for relation in first.extraction_set.relations:
    assert relation.subject_entity_id in entity_ids
    assert relation.object_entity_id in entity_ids

dup_chunk=replace(chunk,text="Alpha Alpha Alpha -> Beta")
dup_set=replace(chunk_set,chunks=(dup_chunk,))
dup=extractor.extract(dup_set,policy)
assert len([e for e in dup.extraction_set.entities if e.canonical_name=="Alpha"])==1

plain_chunk=replace(chunk,text="Alpha and Beta appear together.")
plain_set=replace(chunk_set,chunks=(plain_chunk,))
plain=extractor.extract(plain_set,policy)
assert plain.status=="EXTRACTED"
assert plain.extraction_set.relations==()

v2=extractor.extract(chunk_set,ExtractionPolicy("POL-K5","2.0",min_confidence=0.8))
assert first.extraction_set.extraction_set_hash!=v2.extraction_set.extraction_set_hash

bad_chunk=replace(chunk,source_id="OTHER")
bad=extractor.extract(replace(chunk_set,chunks=(bad_chunk,)),policy)
assert bad.status=="REJECTED"
assert any("source_id mismatch" in x for x in bad.diagnostics)

for entity in first.extraction_set.entities:
    assert 0.0 <= entity.confidence <= 1.0
for relation in first.extraction_set.relations:
    assert 0.0 <= relation.confidence <= 1.0

invalid=extractor.extract(chunk_set,ExtractionPolicy("POL-K5","1.0",min_confidence=1.5))
assert invalid.status=="REJECTED"

payload={
 "valid_chunk_set_extracted":True,
 "deterministic_hashes":True,
 "entity_evidence_preserved":True,
 "relation_evidence_preserved":True,
 "duplicate_entities_deduplicated":True,
 "unsupported_text_no_invented_relation":True,
 "policy_version_changes_identity":True,
 "malformed_lineage_rejected":True,
 "confidence_bounded":True,
 "invalid_policy_rejected":True,
 "referential_integrity_preserved":True,
 "chunk_set_id":chunk_set.chunk_set_id,
 "chunk_set_hash":chunk_set.chunk_set_hash,
 "extraction_set_id":first.extraction_set.extraction_set_id,
 "extraction_set_hash":first.extraction_set.extraction_set_hash,
 "entity_count":len(first.extraction_set.entities),
 "relation_count":len(first.extraction_set.relations),
 "extractor_id":first.extraction_set.extractor_id,
 "extractor_version":first.extraction_set.extractor_version,
 "policy_id":first.extraction_set.policy_id,
 "policy_version":first.extraction_set.policy_version,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Entity/Relation qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @("valid_chunk_set_extracted","deterministic_hashes","entity_evidence_preserved","relation_evidence_preserved","duplicate_entities_deduplicated","unsupported_text_no_invented_relation","policy_version_changes_identity","malformed_lineage_rejected","confidence_bounded","invalid_policy_rejected","referential_integrity_preserved")){
    $result[$name]=[bool]$runtime.$name
  }
  $result.passed=$result.toolchain_ready -and $result.regression -and $result.valid_chunk_set_extracted -and $result.deterministic_hashes -and $result.entity_evidence_preserved -and $result.relation_evidence_preserved -and $result.duplicate_entities_deduplicated -and $result.unsupported_text_no_invented_relation -and $result.policy_version_changes_identity -and $result.malformed_lineage_rejected -and $result.confidence_bounded -and $result.invalid_policy_rejected -and $result.referential_integrity_preserved
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 K5 ENTITY RELATION EXTRACTION: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 K5 ENTITY RELATION EXTRACTION: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
