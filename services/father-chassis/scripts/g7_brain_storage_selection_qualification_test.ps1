param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$date = Get-Date -Format "yyyy-MM-dd"
$artifactPath = Join-Path $artifactDir "g7_brain_storage_selection_qualification_$date.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_BRAIN_STORAGE_SELECTION"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 edge_profile_selected=$false
 explanation_present=$false
 hard_limits_enforced=$false
 evidence_required=$false
 minimal_sufficient_selected=$false
 rejected_alternatives_explained=$false
 ambiguity_explicit=$false
 input_order_independent=$false
 policy_version_changes_identity=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[BRAIN STORAGE] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[BRAIN STORAGE] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:BRAIN_STORAGE_ARTIFACT=$artifactPath

@'
import json, os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from father.brain_factory.storage_selection import (
    DeterministicStorageProfileSelector, StorageProfileDescriptor,
    StorageSelectionPolicy, StorageSelectionRequest
)

artifact_path=Path(os.environ["BRAIN_STORAGE_ARTIFACT"])
selector=DeterministicStorageProfileSelector()
policy=StorageSelectionPolicy("POL-STORAGE","1.0")
req=StorageSelectionRequest(
    "REQ-EDGE","B1","EDGE",("RELATIONAL","OBJECT"),
    10000,1,100,2048,32,True,False,False,True
)
edge=StorageProfileDescriptor(
    "SP-EDGE-LITE",("B1",),("EDGE",),("RELATIONAL","OBJECT"),
    512,2,100000,5,True,False,False,"LOW",1,"QUALIFIED","QUALIFIED"
)

ok=selector.select(req,(edge,),policy)
assert ok.status=="SELECTED" and ok.selection_reasons

assert selector.select(req,(replace(edge,min_ram_mb=4096),),policy).status=="NO_MATCH"
assert selector.select(replace(req,concurrent_users=10),(edge,),policy).status=="NO_MATCH"
assert selector.select(req,(replace(edge,power_class="MEDIUM"),),policy).status=="NO_MATCH"
assert selector.select(req,(replace(edge,evidence_state="MEASURED"),),policy).status=="NO_MATCH"

small=replace(edge,profile_id="SP-SMALL",operational_complexity=1)
large=replace(edge,profile_id="SP-LARGE",operational_complexity=3,min_ram_mb=1024)
preferred=selector.select(req,(large,small),policy)
assert preferred.status=="SELECTED" and preferred.selected_profile_id=="SP-SMALL"

bad=replace(edge,profile_id="SP-BAD",min_ram_mb=4096)
explained=selector.select(req,(bad,small),policy)
assert any(x.profile_id=="SP-BAD" and "ram_ceiling_exceeded" in x.reasons for x in explained.rejected_alternatives)

amb=selector.select(req,(replace(edge,profile_id="SP-A"),replace(edge,profile_id="SP-B")),policy)
assert amb.status=="AMBIGUOUS"

forward=selector.select(req,(large,small),policy)
reverse=selector.select(req,(small,large),policy)
assert forward.decision_hash==reverse.decision_hash

v2=selector.select(req,(edge,),StorageSelectionPolicy("POL-STORAGE","2.0"))
assert ok.decision_hash!=v2.decision_hash

payload={
 "edge_profile_selected":True,
 "explanation_present":True,
 "hard_limits_enforced":True,
 "evidence_required":True,
 "minimal_sufficient_selected":True,
 "rejected_alternatives_explained":True,
 "ambiguity_explicit":True,
 "input_order_independent":True,
 "policy_version_changes_identity":True,
 "selected_profile_id":ok.selected_profile_id,
 "decision_id":ok.decision_id,
 "decision_hash":ok.decision_hash,
 "policy_id":policy.policy_id,
 "policy_version":policy.version,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Brain Storage Selection qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @(
    "edge_profile_selected","explanation_present","hard_limits_enforced",
    "evidence_required","minimal_sufficient_selected",
    "rejected_alternatives_explained","ambiguity_explicit",
    "input_order_independent","policy_version_changes_identity"
  )){
    $result[$name]=[bool]$runtime.$name
  }

  $result.passed=$result.toolchain_ready -and $result.regression -and
    $result.edge_profile_selected -and $result.explanation_present -and
    $result.hard_limits_enforced -and $result.evidence_required -and
    $result.minimal_sufficient_selected -and
    $result.rejected_alternatives_explained -and $result.ambiguity_explicit -and
    $result.input_order_independent -and $result.policy_version_changes_identity
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 BRAIN STORAGE SELECTION: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 BRAIN STORAGE SELECTION: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
