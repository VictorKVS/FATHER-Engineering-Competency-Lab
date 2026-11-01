param(
    [switch]$ApproveDockerContainedProduction
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 FINAL PRODUCTION RELEASE GATE ==="

& $Py -m pytest tests/test_final_release_gate.py -q
if ($LASTEXITCODE -ne 0) { throw "final release gate regression failed" }

$ManifestPath = Join-Path $Repo "factory\chassis\FUA-001\manifest.json"
$Manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

Write-Host ("STATUS                    : {0}" -f $Manifest.status)
Write-Host ("PRODUCTION READY          : {0}" -f $Manifest.production_ready)
Write-Host ("APPROVED PROFILE          : {0}" -f (($Manifest.approved_execution_profiles) -join ", "))
Write-Host ("WINDOWS HOST NATIVE       : {0}" -f $Manifest.windows_host_native_execution)

if (-not $ApproveDockerContainedProduction) {
    Write-Host ""
    Write-Host "FINAL RELEASE DECISION    : BLOCKED_PENDING_HUMAN_DECISION"
    Write-Host "REQUIRED HUMAN ACTION     : Approve DOCKER_CONTAINED_ONLY production release"
    exit 40
}

if ($Manifest.status -ne "PRODUCTION_READINESS_VALIDATED") {
    throw "production readiness must be validated before final release"
}
if ($Manifest.production_readiness_review.status -ne "PASS") {
    throw "production readiness review must be PASS"
}
if ($Manifest.production_readiness_review.finding_count -ne 0) {
    throw "production readiness findings must be zero"
}
if ($Manifest.docker_native_containment_evm.status -ne "PASS") {
    throw "Docker native containment must be PASS"
}
if ($Manifest.approved_execution_profiles -notcontains "DOCKER_CONTAINED_ONLY") {
    throw "DOCKER_CONTAINED_ONLY must be an approved execution profile"
}
if ($Manifest.windows_host_native_execution -ne "NOT_APPROVED") {
    throw "Windows-host native execution must remain NOT_APPROVED"
}

$Manifest.status = "PRODUCTION_RELEASED"
$Manifest.production_ready = $true
$Manifest.next_factory_gates = @()
$Manifest | ConvertTo-Json -Depth 20 | Set-Content $ManifestPath -Encoding UTF8

$EvidencePath = Join-Path $Repo "factory\evidence\EVID-FUA-FINAL-PRODUCTION-RELEASE-0024.md"
@"
# FUA-001 Final Production Release 0024

Evidence ID: EVID-FUA-FINAL-PRODUCTION-RELEASE-0024
Date: 2026-11-01
Decision: APPROVED

Approved execution profile: DOCKER_CONTAINED_ONLY
Windows-host native execution: NOT_APPROVED
Production readiness review: PASS
Finding count: 0
Production ready: true

This release authorizes production use only under the approved Docker-contained execution profile.
"@ | Set-Content $EvidencePath -Encoding UTF8

Write-Host ""
Write-Host "FINAL RELEASE DECISION    : PASS"
Write-Host "STATUS                    : PRODUCTION_RELEASED"
Write-Host "PRODUCTION READY          : True"
Write-Host "PROFILE                   : DOCKER_CONTAINED_ONLY"
Write-Host "WINDOWS HOST NATIVE       : NOT_APPROVED"
Write-Host ("EVIDENCE                  : {0}" -f $EvidencePath)
