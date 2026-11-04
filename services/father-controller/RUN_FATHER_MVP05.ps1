$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-05 / UNIFIED BENCH ===" -ForegroundColor Cyan
python --version
python -m compileall father run_factory_mvp05.py
if ($LASTEXITCODE -ne 0) { throw "MVP-05 syntax check failed" }
python .\run_factory_mvp05.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-05 failed" }
Write-Host "=== FATHER FACTORY MVP-05: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp05_unified_bench.json"
