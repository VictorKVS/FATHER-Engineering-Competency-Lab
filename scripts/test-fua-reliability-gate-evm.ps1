$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 RELIABILITY GATE EVM ==="

Write-Host ""
Write-Host "01. Deterministic reliability regression suite"
$tests = @(
    "tests/test_audit.py",
    "tests/test_evidence.py",
    "tests/test_approval.py",
    "tests/test_recovery.py",
    "tests/test_resources.py",
    "tests/test_context_manager.py",
    "tests/test_compatibility.py",
    "tests/test_reliability_failure_injection.py",
    "tests/test_reliability_stress.py",
    "tests/test_process_sandbox.py",
    "tests/test_tools_runtime.py",
    "tests/test_human_acceptance.py"
)
& $Py -m pytest @tests -q
if ($LASTEXITCODE -ne 0) {
    throw "reliability regression suite failed"
}
Write-Host "RELIABILITY TESTS : PASS"

Write-Host ""
Write-Host "02. Windows Job Object resource limits"
& (Join-Path $PSScriptRoot "test-fua-sandbox-resource-limits-evm.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "sandbox resource limits failed"
}
Write-Host "RESOURCE LIMITS   : PASS"

Write-Host ""
Write-Host "03. Final repository evidence audit"
& (Join-Path $PSScriptRoot "test-fua-final-evidence-audit.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "final evidence audit failed"
}
Write-Host "EVIDENCE AUDIT    : PASS"

Write-Host ""
Write-Host "04. Current release state"
$Manifest = Get-Content (Join-Path $Repo "factory\chassis\FUA-001\manifest.json") -Raw | ConvertFrom-Json
Write-Host ("INSTALL PERMIT    : {0}" -f $Manifest.installation_permit)
Write-Host ("PRODUCTION READY  : {0}" -f $Manifest.production_ready)
Write-Host ("NEXT GATES        : {0}" -f (($Manifest.next_factory_gates) -join ", "))

$TestingStatuses = @(
    "INSTALLATION_APPROVED_FOR_TESTING",
    "PRODUCT_TEST_IN_PROGRESS",
    "PRODUCT_TEST_VALIDATED",
    "PILOT_TEST_IN_PROGRESS",
    "PILOT_TEST_VALIDATED",
    "PRODUCTION_READINESS_REVIEW"
)

if ($Manifest.status -eq "PRODUCTION_RELEASED") {
    if ($Manifest.installation_permit -ne "PASS") {
        throw "production phase requires installation permit PASS"
    }
    if ($Manifest.production_ready -ne $true) {
        throw "production phase requires production_ready=true"
    }
    if ($Manifest.approved_execution_profiles -notcontains "DOCKER_CONTAINED_ONLY") {
        throw "production phase requires DOCKER_CONTAINED_ONLY profile"
    }
    if ($Manifest.windows_host_native_execution -ne "NOT_APPROVED") {
        throw "production phase requires Windows host native execution NOT_APPROVED"
    }
    Write-Host "RELEASE PHASE     : PRODUCTION"
}
elseif ($TestingStatuses -contains $Manifest.status) {
    if ($Manifest.installation_permit -ne "PASS") {
        throw "testing phase requires installation permit PASS"
    }
    if ($Manifest.production_ready -ne $false) {
        throw "testing phase requires production_ready=false"
    }
    Write-Host "RELEASE PHASE     : CONTROLLED_TESTING"
}
else {
    if ($Manifest.installation_permit -ne "DENIED") {
        throw "pre-acceptance phase requires installation permit DENIED"
    }
    if ($Manifest.production_ready -ne $false) {
        throw "pre-acceptance phase requires production_ready=false"
    }
    Write-Host "RELEASE PHASE     : PRE_ACCEPTANCE"
}

Write-Host ""
Write-Host "FUA-001 RELIABILITY GATE RESULT: PASS"
