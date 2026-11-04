$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-09 / MODEL MATRIX ECONOMICS LEAGUE ===" -ForegroundColor Cyan
python --version
python -m compileall father design_studio_server.py run_factory_mvp09.py
if ($LASTEXITCODE -ne 0) { throw "MVP-09 syntax check failed" }
python .\run_factory_mvp09.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-09 failed" }
Write-Host "=== FATHER FACTORY MVP-09: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp09_model_matrix.json"
Write-Host "Open UI: .\START_FATHER_DESIGN_STUDIO.ps1" -ForegroundColor Yellow
