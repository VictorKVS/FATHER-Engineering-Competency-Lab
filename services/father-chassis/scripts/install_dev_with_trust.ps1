param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$trustDir = Join-Path $repoRoot "projects\FATHER-TRUST-COMPETENCY-0001"
$chassisDir = Join-Path $repoRoot "services\father-chassis"

Write-Host "[FATHER DEV] Install Trust Competency package"
Push-Location $trustDir
try {
    & $Python -m pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}

Write-Host "[FATHER DEV] Install father-chassis package"
Push-Location $chassisDir
try {
    & $Python -m pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}

Write-Host "[FATHER DEV] Verify Trust public API"
& $Python -c "from trust_competency import CompetencyEvaluator, CompetencyPolicy, Claim, EvidenceRecord; print('TRUST_API_READY')"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "FATHER DEV WITH TRUST: READY"
