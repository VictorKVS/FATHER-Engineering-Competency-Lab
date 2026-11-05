$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER EXECUTION TELEMETRY + ESCALATION MVP-05 ===" -ForegroundColor Cyan
python .\run_execution_escalation_mvp05.py
if($LASTEXITCODE -ne 0){ throw "Execution Escalation MVP-05 failed" }
Write-Host "=== EXECUTION TELEMETRY + ESCALATION MVP-05: PASS ===" -ForegroundColor Green
