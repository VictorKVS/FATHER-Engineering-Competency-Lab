param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$repoRoot = Resolve-Path (Join-Path $serviceDir "..\..")
$trustDir = Join-Path $repoRoot "projects\FATHER-TRUST-COMPETENCY-0001"
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_m5a_trust_integration_packaging_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result = [ordered]@{
 qualification="G7_M5A_TRUST_INTEGRATION_PACKAGING"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 trust_install=$false
 chassis_install=$false
 trust_api=$false
 trust_tests=$false
 chassis_tests=$false
 cross_package_call=$false
 passed=$false
}

try {
 Push-Location $repoRoot
 try {
  Write-Host "[G7 M5A] Install Trust package"
  & $Python -m pip install -e "projects/FATHER-TRUST-COMPETENCY-0001[dev]"
  if($LASTEXITCODE -ne 0){ throw "Trust install failed" }
  $result.trust_install=$true

  Write-Host "[G7 M5A] Install chassis package"
  & $Python -m pip install -e "services/father-chassis[dev]"
  if($LASTEXITCODE -ne 0){ throw "Chassis install failed" }
  $result.chassis_install=$true

  Write-Host "[G7 M5A] Verify Trust public API"
  & $Python -c "from trust_competency import CompetencyEvaluator,CompetencyPolicy,Claim,EvidenceRecord; print('TRUST_API_READY')"
  if($LASTEXITCODE -ne 0){ throw "Trust API check failed" }
  $result.trust_api=$true

  Write-Host "[G7 M5A] Run Trust independent tests"
  Push-Location $trustDir
  try { & $Python -m pytest -q }
  finally { Pop-Location }
  if($LASTEXITCODE -ne 0){ throw "Trust tests failed" }
  $result.trust_tests=$true

  Write-Host "[G7 M5A] Run chassis regression"
  Push-Location $serviceDir
  try { & $Python -m pytest -q }
  finally { Pop-Location }
  if($LASTEXITCODE -ne 0){ throw "Chassis tests failed" }
  $result.chassis_tests=$true

  Write-Host "[G7 M5A] Cross-package evaluator call"
  & $Python -c "from trust_competency import CompetencyEvaluator,CompetencyPolicy,Claim,EvidenceRecord; c=Claim('C','A','d','cap','C3'); e=(EvidenceRecord('E','A','C','qualification','x','h','2026-11-13T00:00:00Z','test'),); r=CompetencyEvaluator().qualify(claim=c,evidence=e,policy=CompetencyPolicy('C3',1,frozenset({'qualification'}))); assert r.qualified; print(r.qualification_id)"
  if($LASTEXITCODE -ne 0){ throw "Cross-package evaluator call failed" }
  $result.cross_package_call=$true
  $result.passed=$true
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 M5A TRUST INTEGRATION PACKAGING: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 M5A TRUST INTEGRATION PACKAGING: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
