$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.8 / STAGE 19 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage19.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Release Manifest + Compatibility Matrix proof" -ForegroundColor Yellow
python run_stage19.py
if ($LASTEXITCODE -ne 0) { throw "Stage 19 failed" }

Write-Host "`n=== FATHER CHASSIS v2.8: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage19_evidence.json"
Write-Host "Release manifest: evidence\stage19_release_manifest.json"
