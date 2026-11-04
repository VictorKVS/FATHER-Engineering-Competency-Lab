$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-03 / DESIGN STUDIO DATA MODEL ===" -ForegroundColor Cyan
python --version
python -m compileall father run_factory_mvp03.py
if ($LASTEXITCODE -ne 0) { throw "MVP-03 syntax check failed" }
python .\run_factory_mvp03.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-03 failed" }
Write-Host "=== FATHER FACTORY MVP-03: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp03_design_studio_model.json"


Write-Host ""
Write-Host "=== HANDOFF TO FACTORY MVP-04 ===" -ForegroundColor Cyan
& .\RUN_FATHER_MVP04.ps1
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-04 failed" }
