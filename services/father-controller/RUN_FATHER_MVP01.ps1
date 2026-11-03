$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-01 / AGENT ZOO ===" -ForegroundColor Cyan
python --version
python -m compileall father run_factory_mvp01.py
if ($LASTEXITCODE -ne 0) { throw "MVP-01 syntax check failed" }
python .\run_factory_mvp01.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-01 failed" }
Write-Host "=== FATHER FACTORY MVP-01: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp01_agent_zoo.json"
