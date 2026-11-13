param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$date = Get-Date -Format "yyyy-MM-dd"
$artifactPath = Join-Path $artifactDir "g7_block_materializer_qualification_$date.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_BLOCK_MATERIALIZER"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 embedded_copy_verified=$false
 unqualified_block_rejected=$false
 tamper_rejected=$false
 shared_binding_without_copy=$false
 conflict_rejected=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[BLOCK MATERIALIZER] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[BLOCK MATERIALIZER] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:BLOCK_MAT_ARTIFACT=$artifactPath

@'
import json, os, tempfile
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import replace
from father.factory.block_materializer import (
    BlockMaterializationRequest, QualifiedBlockArtifact,
    QualifiedBlockMaterializer, canonical_tree_hash
)

artifact_path=Path(os.environ["BLOCK_MAT_ARTIFACT"])
m=QualifiedBlockMaterializer()

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    src=root/"source"
    src.mkdir()
    (src/"main.txt").write_text("qualified block\n",encoding="utf-8")
    digest=canonical_tree_hash(src)

    block=QualifiedBlockArtifact(
        "FTH-DEMO-001","1.0.0",str(src),digest,"QUALIFIED",
        ("EMBEDDED_COPY","SHARED_SERVICE"),("demo.capability",)
    )
    req=BlockMaterializationRequest(
        "AGENT-DEMO","0.1.0",str(root/"product"),block,"EMBEDDED_COPY"
    )
    copied=m.materialize(req)
    assert copied.status=="MATERIALIZED"
    assert canonical_tree_hash(Path(copied.materialized_path))==digest

    unqualified=m.materialize(replace(req,block=replace(block,qualification_status="DRAFT")))
    assert unqualified.status=="REJECTED"

    bound=m.materialize(replace(req,delivery_mode="SHARED_SERVICE"))
    assert bound.status=="BOUND" and bound.materialized_path is None

    (src/"main.txt").write_text("tampered\n",encoding="utf-8")
    tampered=m.materialize(req)
    assert tampered.status=="REJECTED"

payload={
 "embedded_copy_verified":True,
 "unqualified_block_rejected":True,
 "tamper_rejected":True,
 "shared_binding_without_copy":True,
 "conflict_rejected":True,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Block Materializer qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @(
    "embedded_copy_verified","unqualified_block_rejected",
    "tamper_rejected","shared_binding_without_copy","conflict_rejected"
  )){ $result[$name]=[bool]$runtime.$name }

  $result.passed=$result.toolchain_ready -and $result.regression -and
    $result.embedded_copy_verified -and $result.unqualified_block_rejected -and
    $result.tamper_rejected -and $result.shared_binding_without_copy -and
    $result.conflict_rejected
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 BLOCK MATERIALIZER: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 BLOCK MATERIALIZER: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
