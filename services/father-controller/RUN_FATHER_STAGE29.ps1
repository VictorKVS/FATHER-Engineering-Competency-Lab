$ErrorActionPreference = "Stop"
Write-Host "=== FATHER ADAPTIVE BRAIN ROUTER / STAGE 29 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage29.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage29.py
if ($LASTEXITCODE -ne 0) { throw "Stage 29 failed" }
Write-Host "=== FATHER ADAPTIVE BRAIN ROUTER: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage29_adaptive_brain_router.json"
Write-Host "=== ARCHITECTURE CYCLE 0-29 COMPLETE ===" -ForegroundColor Green
