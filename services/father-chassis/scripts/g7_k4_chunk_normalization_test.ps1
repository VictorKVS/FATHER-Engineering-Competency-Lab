param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_k4_chunk_normalization_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_K4_CHUNK_NORMALIZATION"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 valid_document_chunked=$false
 deterministic_hashes=$false
 whitespace_normalized=$false
 lineage_preserved=$false
 locators_preserved=$false
 no_empty_chunks=$false
 max_chars_respected=$false
 oversize_split_deterministic=$false
 policy_version_changes_identity=$false
 cross_document_rejected=$false
 overlap_policy_rejected=$false
 no_semantic_rewrite=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[G7 K4] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[G7 K4] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:G7_K4_ARTIFACT=$artifactPath

@'
import json, os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from father.knowledge_factory.chunk_normalization import (
    ChunkPolicy,
    DeterministicStructuralChunker,
)
from father.knowledge_factory.structural_parser import (
    StructuralDocument,
    StructuralUnit,
)

artifact_path=Path(os.environ["G7_K4_ARTIFACT"])

units=(
    StructuralUnit("UNIT-000000",0,"heading","# TITLE","line:1-1","SRC-K4","a"*64),
    StructuralUnit("UNIT-000001",1,"paragraph","First    paragraph   with   extra whitespace.","line:3-3","SRC-K4","a"*64),
    StructuralUnit("UNIT-000002",2,"paragraph","Second paragraph.","line:5-5","SRC-K4","a"*64),
)
document=StructuralDocument(
    document_id="DOC-K4",
    source_id="SRC-K4",
    source_content_hash="a"*64,
    provenance_id="PRV-K4",
    parser_id="FTH-TEXT-STRUCTURAL-PARSER",
    parser_version="1.0.0",
    units=units,
    document_hash="b"*64,
)
chunker=DeterministicStructuralChunker()
policy=ChunkPolicy("POL-K4","1.0",max_chars=120)

first=chunker.chunk(document,policy)
second=chunker.chunk(document,policy)
assert first.status=="CHUNKED"
assert second.status=="CHUNKED"
assert first.chunk_set.chunk_set_hash==second.chunk_set.chunk_set_hash
assert [c.chunk_hash for c in first.chunk_set.chunks]==[c.chunk_hash for c in second.chunk_set.chunks]

joined=" ".join(c.text for c in first.chunk_set.chunks)
assert "First paragraph with extra whitespace." in joined
assert "Second paragraph." in joined
assert "First    paragraph" not in joined

for chunk in first.chunk_set.chunks:
    assert chunk.source_id==document.source_id
    assert chunk.document_id==document.document_id
    assert chunk.document_hash==document.document_hash
    assert chunk.text.strip()
    assert len(chunk.text)<=policy.max_chars
    assert chunk.source_unit_ids
    assert chunk.source_locators

long_text="word "*50
long_doc=replace(
    document,
    units=(
        units[0],
        replace(units[1],text=long_text),
    ),
)
small=ChunkPolicy("POL-K4","1.0",max_chars=40)
long_first=chunker.chunk(long_doc,small)
long_second=chunker.chunk(long_doc,small)
assert long_first.status=="CHUNKED"
assert len(long_first.chunk_set.chunks)>1
assert [c.text for c in long_first.chunk_set.chunks]==[c.text for c in long_second.chunk_set.chunks]
assert all(len(c.text)<=small.max_chars for c in long_first.chunk_set.chunks)

v2=chunker.chunk(document,ChunkPolicy("POL-K4","2.0",max_chars=120))
assert first.chunk_set.chunk_set_hash!=v2.chunk_set.chunk_set_hash

bad_doc=replace(document,units=(units[0],replace(units[1],source_id="OTHER")))
bad=chunker.chunk(bad_doc,policy)
assert bad.status=="REJECTED"
assert any("source_id mismatch" in x for x in bad.diagnostics)

overlap=chunker.chunk(document,ChunkPolicy("POL-K4","1.0",overlap_chars=10))
assert overlap.status=="REJECTED"

payload={
 "valid_document_chunked":True,
 "deterministic_hashes":True,
 "whitespace_normalized":True,
 "lineage_preserved":True,
 "locators_preserved":True,
 "no_empty_chunks":True,
 "max_chars_respected":True,
 "oversize_split_deterministic":True,
 "policy_version_changes_identity":True,
 "cross_document_rejected":True,
 "overlap_policy_rejected":True,
 "no_semantic_rewrite":True,
 "source_id":document.source_id,
 "document_id":document.document_id,
 "document_hash":document.document_hash,
 "chunk_set_id":first.chunk_set.chunk_set_id,
 "chunk_set_hash":first.chunk_set.chunk_set_hash,
 "chunk_count":len(first.chunk_set.chunks),
 "normalizer_id":first.chunk_set.normalizer_id,
 "normalizer_version":first.chunk_set.normalizer_version,
 "policy_id":first.chunk_set.policy_id,
 "policy_version":first.chunk_set.policy_version,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Chunk normalization qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @("valid_document_chunked","deterministic_hashes","whitespace_normalized","lineage_preserved","locators_preserved","no_empty_chunks","max_chars_respected","oversize_split_deterministic","policy_version_changes_identity","cross_document_rejected","overlap_policy_rejected","no_semantic_rewrite")){
    $result[$name]=[bool]$runtime.$name
  }
  $result.passed=$result.toolchain_ready -and $result.regression -and $result.valid_document_chunked -and $result.deterministic_hashes -and $result.whitespace_normalized -and $result.lineage_preserved -and $result.locators_preserved -and $result.no_empty_chunks -and $result.max_chars_respected -and $result.oversize_split_deterministic -and $result.policy_version_changes_identity -and $result.cross_document_rejected -and $result.overlap_policy_rejected -and $result.no_semantic_rewrite
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 K4 CHUNK NORMALIZATION: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 K4 CHUNK NORMALIZATION: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
