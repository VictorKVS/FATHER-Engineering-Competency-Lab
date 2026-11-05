$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER SEMANTIC ESCALATION RUNTIME MVP-07 ===" -ForegroundColor Cyan
python .\run_semantic_escalation_runtime_mvp07.py
if($LASTEXITCODE -ne 0){ throw "Semantic Escalation Runtime MVP-07 failed" }
Write-Host "=== SEMANTIC ESCALATION RUNTIME MVP-07: PASS ===" -ForegroundColor Green
