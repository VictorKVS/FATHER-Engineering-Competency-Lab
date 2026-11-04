$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-02 / BLOCK CONTRACT ===" -ForegroundColor Cyan
python --version
python -m compileall father run_factory_mvp02.py
if ($LASTEXITCODE -ne 0) { throw "MVP-02 syntax check failed" }
python .\run_factory_mvp02.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-02 failed" }
Write-Host "=== FATHER FACTORY MVP-02: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp02_block_contract.json"


Write-Host ""
Write-Host "=== HANDOFF TO FACTORY MVP-03 ===" -ForegroundColor Cyan
& .\RUN_FATHER_MVP03.ps1
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-03 failed" }
