$ErrorActionPreference = "Stop"
Write-Host "=== FATHER PRODUCT FACTORY / STAGE 26 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage26.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage26.py
if ($LASTEXITCODE -ne 0) { throw "Stage 26 failed" }
Write-Host "=== FATHER PRODUCT FACTORY: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage26_product_factory.json"
