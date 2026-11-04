$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-04 / AUTO ASSEMBLY ===" -ForegroundColor Cyan
python --version
python -m compileall father run_factory_mvp04.py
if ($LASTEXITCODE -ne 0) { throw "MVP-04 syntax check failed" }
python .\run_factory_mvp04.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-04 failed" }
Write-Host "=== FATHER FACTORY MVP-04: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp04_auto_assembly.json"


Write-Host ""
Write-Host "=== HANDOFF TO FACTORY MVP-05 ===" -ForegroundColor Cyan
& .\RUN_FATHER_MVP05.ps1
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-05 failed" }
