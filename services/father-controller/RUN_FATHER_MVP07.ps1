$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-07 / DESIGN STUDIO UI ===" -ForegroundColor Cyan
python --version
python -m compileall father design_studio_server.py run_factory_mvp07.py
if ($LASTEXITCODE -ne 0) { throw "MVP-07 syntax check failed" }
python .\run_factory_mvp07.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-07 failed" }
Write-Host "=== FATHER FACTORY MVP-07: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp07_design_studio_ui.json"
Write-Host "Start UI: .\START_FATHER_DESIGN_STUDIO.ps1" -ForegroundColor Yellow


Write-Host ""
Write-Host "=== HANDOFF TO FACTORY MVP-08 ===" -ForegroundColor Cyan
& .\RUN_FATHER_MVP08.ps1
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-08 failed" }
