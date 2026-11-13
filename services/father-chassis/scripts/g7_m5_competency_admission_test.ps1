param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_m5_competency_admission_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_M5_COMPETENCY_ADMISSION"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 trust_tests=$false
 qualified_admitted=$false
 underqualified_blocked=$false
 missing_evidence_blocked=$false
 trust_trace_preserved=$false
 strict_mode_fail_closed=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  & $Python -c "import trust_competency"
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: trust_competency missing; run scripts\install_dev_with_trust.ps1" }
  $result.toolchain_ready=$true

  Write-Host "[G7 M5] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[G7 M5] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Chassis regression failed" }
  $result.regression=$true

  Write-Host "[G7 M5] Trust tests"
  Push-Location (Resolve-Path "..\..\projects\FATHER-TRUST-COMPETENCY-0001")
  try { & $Python -m pytest -q }
  finally { Pop-Location }
  if($LASTEXITCODE -ne 0){ throw "Trust tests failed" }
  $result.trust_tests=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:G7_M5_ARTIFACT=$artifactPath
@'
import json, os
from datetime import datetime, timezone
from pathlib import Path
from trust_competency import Claim, EvidenceRecord
from father.engineering.competency_admission import CompetencyAdmissionGate,InMemoryTrustCompetencySource,StageCompetencyPolicy
from father.engineering.factory_orchestrator import FactoryEngineeringWorkflow,StageArtifact
from father.engineering.stage_artifacts import CustomerRequestPayload
from father.engineering.delivery_contract import BusinessProcessSpec

artifact_path=Path(os.environ["G7_M5_ARTIFACT"])

def ev(eid,agent,claim,etype):
    return EvidenceRecord(eid,agent,claim,etype,eid+".json",eid,"2026-11-13T00:00:00+00:00","qualification")

policy=StageCompetencyPolicy("BUSINESS_ANALYSIS","business_analysis","process_design","C3",2,frozenset({"implementation","qualification"}))

def run(level,evidence):
    claim=Claim("CLM-BA", "FTH-AGENT-BUSINESS-ANALYST","business_analysis","process_design",level)
    gate=CompetencyAdmissionGate(source=InMemoryTrustCompetencySource((claim,),evidence(claim)),policies=(policy,))
    wf=FactoryEngineeringWorkflow(competency_gate=gate,require_competency_admission=True)
    wf.add_external_artifact(StageArtifact("REQ","customer_request","HUMAN_APPROVAL",CustomerRequestPayload("REQ","t","o"),True))
    return wf.submit_stage_artifact("BUSINESS_ANALYSIS",StageArtifact("BP","BusinessProcessSpec","FTH-AGENT-BUSINESS-ANALYST",BusinessProcessSpec("BP","g",("i",),("o",),("a",),approved=True),True))

qualified=run("C3",lambda c:(ev("E1",c.subject_id,c.claim_id,"implementation"),ev("E2",c.subject_id,c.claim_id,"qualification")))
assert qualified.status=="PASS"
assert qualified.competency_qualification_id=="QUAL-CLM-BA-C3"
assert qualified.competency_evidence_ids==("E1","E2")

under=run("C1",lambda c:(ev("E1",c.subject_id,c.claim_id,"implementation"),ev("E2",c.subject_id,c.claim_id,"qualification")))
assert under.status=="BLOCKED"

missing=run("C3",lambda c:(ev("E1",c.subject_id,c.claim_id,"implementation"),))
assert missing.status=="BLOCKED"

strict=False
try:
    FactoryEngineeringWorkflow(require_competency_admission=True)
except ValueError:
    strict=True
assert strict

payload={
 "qualified_admitted":True,
 "underqualified_blocked":True,
 "missing_evidence_blocked":True,
 "trust_trace_preserved":True,
 "strict_mode_fail_closed":True,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Competency integration qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  $result.qualified_admitted=[bool]$runtime.qualified_admitted
  $result.underqualified_blocked=[bool]$runtime.underqualified_blocked
  $result.missing_evidence_blocked=[bool]$runtime.missing_evidence_blocked
  $result.trust_trace_preserved=[bool]$runtime.trust_trace_preserved
  $result.strict_mode_fail_closed=[bool]$runtime.strict_mode_fail_closed
  $result.passed=$result.toolchain_ready -and $result.regression -and $result.trust_tests -and $result.qualified_admitted -and $result.underqualified_blocked -and $result.missing_evidence_blocked -and $result.trust_trace_preserved -and $result.strict_mode_fail_closed
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 M5 COMPETENCY ADMISSION: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 M5 COMPETENCY ADMISSION: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
