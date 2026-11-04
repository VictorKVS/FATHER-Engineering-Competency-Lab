$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-04 / AUTO ASSEMBLY ===" -ForegroundColor Cyan
python --version
python -m compileall father run_factory_mvp04.py
if ($LASTEXITCODE -ne 0) { throw "MVP-04 syntax check failed" }
python .\run_factory_mvp04.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-04 failed" }
Write-Host "=== FATHER FACTORY MVP-04: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp04_auto_assembly.json"
