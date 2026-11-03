$ErrorActionPreference = "Stop"
Write-Host "=== FATHER BLOCK REGISTRY / STAGE 27 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage27.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage27.py
if ($LASTEXITCODE -ne 0) { throw "Stage 27 failed" }
Write-Host "=== FATHER BLOCK REGISTRY: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage27_block_registry.json"
