$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 PRODUCTION READINESS REVIEW ==="

& $Py -m pytest tests/test_production_readiness.py -q
if ($LASTEXITCODE -ne 0) { throw "production readiness regression tests failed" }

$TempPy = Join-Path $env:TEMP "fua-production-readiness-review.py"
@'
from pathlib import Path
from father_fua.production_readiness import review_production_readiness, production_readiness_decision

root=Path(".")
findings=review_production_readiness(root)
for f in findings:
    print(f"{f.severity} {f.code} {f.status}: {f.message}")
print()
print("FINDING COUNT              :",len(findings))
print("PRODUCTION READINESS RESULT:",production_readiness_decision(root))
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) { throw "production readiness review failed" }

$Manifest = Get-Content (Join-Path $Repo "factory\chassis\FUA-001\manifest.json") -Raw | ConvertFrom-Json
if ($Manifest.production_ready -ne $false) {
    throw "production_ready must remain false"
}

Write-Host ""
Write-Host "FUA-001 PRODUCTION READINESS REVIEW: COMPLETE"
