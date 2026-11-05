$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER RUNTIME EXECUTION MVP-04 ===" -ForegroundColor Cyan
python .\run_runtime_execution_mvp04.py
if($LASTEXITCODE -ne 0){ throw "Runtime Execution MVP-04 failed" }
Write-Host "=== RUNTIME EXECUTION MVP-04: PASS ===" -ForegroundColor Green
