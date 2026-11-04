$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-08 / MODEL INTELLIGENCE ===" -ForegroundColor Cyan
python --version
python -m compileall father design_studio_server.py run_factory_mvp08.py
if ($LASTEXITCODE -ne 0) { throw "MVP-08 syntax check failed" }
python .\run_factory_mvp08.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-08 failed" }
Write-Host "=== FATHER FACTORY MVP-08: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp08_model_intelligence.json"
Write-Host "Open UI: .\START_FATHER_DESIGN_STUDIO.ps1" -ForegroundColor Yellow


Write-Host ""
Write-Host "=== HANDOFF TO FACTORY MVP-09 ===" -ForegroundColor Cyan
& .\RUN_FATHER_MVP09.ps1
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-09 failed" }
