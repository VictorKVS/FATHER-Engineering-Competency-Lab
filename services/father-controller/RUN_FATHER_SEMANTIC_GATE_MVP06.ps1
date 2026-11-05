$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER SEMANTIC ACCEPTANCE GATE / CRITIC MVP-06 ===" -ForegroundColor Cyan
python .\run_semantic_acceptance_gate_mvp06.py
if($LASTEXITCODE -ne 0){ throw "Semantic Acceptance Gate MVP-06 failed" }
Write-Host "=== SEMANTIC ACCEPTANCE GATE MVP-06: PASS ===" -ForegroundColor Green
