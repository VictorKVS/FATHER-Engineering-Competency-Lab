param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$date = Get-Date -Format "yyyy-MM-dd"
$artifactPath = Join-Path $artifactDir "g7_brain_supply_qualification_$date.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_BRAIN_SUPPLY_RESOLVER"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 exact_binding=$false
 wrong_class_blocked=$false
 capability_gap_blocked=$false
 domain_role_mode_enforced=$false
 classification_blocked=$false
 cross_tenant_blocked=$false
 revoked_blocked=$false
 ambiguity_explicit=$false
 input_order_independent=$false
 policy_version_changes_identity=$false
 no_silent_class_fallback=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[BRAIN SUPPLY] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[BRAIN SUPPLY] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:BRAIN_SUPPLY_ARTIFACT=$artifactPath

@'
import json, os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from father.brain_factory.supply import (
    AgentBrainRequest,
    BrainPackageDescriptor,
    BrainSupplyPolicy,
    DeterministicBrainSupplyResolver,
)

artifact_path=Path(os.environ["BRAIN_SUPPLY_ARTIFACT"])
resolver=DeterministicBrainSupplyResolver()
policy=BrainSupplyPolicy("POL-BRAIN-SUPPLY","1.0")

req=AgentBrainRequest(
    "REQ-Q","AGENT-Q","B3","ANALYST",("SECURITY",),
    ("VECTOR","GRAPH"),"TASK_SCOPED","TENANT-A",("PUBLIC","INTERNAL")
)
pkg=BrainPackageDescriptor(
    "FBP-SEC-Q","1.0.0","B3",("SECURITY","OSINT"),
    ("VECTOR","GRAPH","LEXICAL"),("BASELINE","TASK_SCOPED"),
    ("B3",),("ANALYST",),"INTERNAL","TENANT-A","QUALIFIED"
)

ok=resolver.resolve(req,(pkg,),policy)
assert ok.status=="BOUND"

wrong_class=resolver.resolve(req,(replace(pkg,brain_class="B4"),),policy)
assert wrong_class.status=="NO_MATCH"

cap_gap=resolver.resolve(req,(replace(pkg,capabilities=("VECTOR",)),),policy)
assert cap_gap.status=="NO_MATCH"

wrong_domain=resolver.resolve(req,(replace(pkg,domains=("LEGAL",)),),policy)
wrong_role=resolver.resolve(req,(replace(pkg,allowed_roles=("ADMIN",)),),policy)
wrong_mode=resolver.resolve(req,(replace(pkg,supported_supply_modes=("BASELINE",)),),policy)
assert all(x.status=="NO_MATCH" for x in (wrong_domain,wrong_role,wrong_mode))

classification=resolver.resolve(req,(replace(pkg,classification="CONFIDENTIAL"),),policy)
assert classification.status=="NO_MATCH"

tenant=resolver.resolve(req,(replace(pkg,tenant_scope="TENANT-B"),),policy)
assert tenant.status=="NO_MATCH"

revoked=resolver.resolve(req,(replace(pkg,lifecycle_state="REVOKED"),),policy)
assert revoked.status=="NO_MATCH"

a=replace(pkg,package_id="FBP-A",capabilities=("VECTOR","GRAPH"))
b=replace(pkg,package_id="FBP-B",capabilities=("VECTOR","GRAPH"))
amb=resolver.resolve(req,(a,b),policy)
assert amb.status=="AMBIGUOUS"

exact=replace(pkg,package_id="FBP-EXACT",capabilities=("VECTOR","GRAPH"))
broad=replace(pkg,package_id="FBP-BROAD",capabilities=("VECTOR","GRAPH","LEXICAL"))
forward=resolver.resolve(req,(broad,exact),policy)
reverse=resolver.resolve(req,(exact,broad),policy)
assert forward.status==reverse.status=="BOUND"
assert forward.selected_package_id==reverse.selected_package_id=="FBP-EXACT"
assert forward.decision_hash==reverse.decision_hash

v2=resolver.resolve(req,(pkg,),BrainSupplyPolicy("POL-BRAIN-SUPPLY","2.0"))
assert ok.decision_hash!=v2.decision_hash

higher=resolver.resolve(req,(replace(pkg,brain_class="B4",compatible_agent_classes=("B3",)),),policy)
assert higher.status=="NO_MATCH"

payload={
 "exact_binding":True,
 "wrong_class_blocked":True,
 "capability_gap_blocked":True,
 "domain_role_mode_enforced":True,
 "classification_blocked":True,
 "cross_tenant_blocked":True,
 "revoked_blocked":True,
 "ambiguity_explicit":True,
 "input_order_independent":True,
 "policy_version_changes_identity":True,
 "no_silent_class_fallback":True,
 "decision_id":ok.decision_id,
 "decision_hash":ok.decision_hash,
 "selected_package_id":ok.selected_package_id,
 "policy_id":policy.policy_id,
 "policy_version":policy.version,
 "completed_at_utc":datetime.now(timezone.utc).isoformat(),
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Brain Supply qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @(
    "exact_binding","wrong_class_blocked","capability_gap_blocked",
    "domain_role_mode_enforced","classification_blocked","cross_tenant_blocked",
    "revoked_blocked","ambiguity_explicit","input_order_independent",
    "policy_version_changes_identity","no_silent_class_fallback"
  )){
    $result[$name]=[bool]$runtime.$name
  }

  $result.passed=$result.toolchain_ready -and $result.regression -and
    $result.exact_binding -and $result.wrong_class_blocked -and
    $result.capability_gap_blocked -and $result.domain_role_mode_enforced -and
    $result.classification_blocked -and $result.cross_tenant_blocked -and
    $result.revoked_blocked -and $result.ambiguity_explicit -and
    $result.input_order_independent -and $result.policy_version_changes_identity -and
    $result.no_silent_class_fallback
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 BRAIN SUPPLY RESOLVER: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 BRAIN SUPPLY RESOLVER: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
