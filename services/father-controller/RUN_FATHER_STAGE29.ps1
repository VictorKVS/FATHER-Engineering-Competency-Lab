$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER ADAPTIVE BRAIN ROUTER / STAGE 29 ===" -ForegroundColor Cyan

& ./TEST_FATHER_OLLAMA.ps1
if ($LASTEXITCODE -ne 0) {
  Write-Host "Ollama preflight failed. Attempting one recovery..." -ForegroundColor Yellow
  & ./TEST_FATHER_OLLAMA.ps1 -Recover
  if ($LASTEXITCODE -ne 0) { throw "Ollama preflight/recovery failed" }
}

python --version
python -m compileall father run_stage29.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

python ./run_stage29.py
if ($LASTEXITCODE -ne 0) { throw "Stage 29 failed" }

Write-Host "=== FATHER ADAPTIVE BRAIN ROUTER: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence/stage29_adaptive_brain_router.json"
Write-Host "=== ARCHITECTURE CYCLE 0-29 COMPLETE ===" -ForegroundColor Green

Write-Host ""
Write-Host "=== HANDOFF TO FACTORY MVP-01 ===" -ForegroundColor Cyan
& ./RUN_FATHER_MVP01.ps1
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-01 failed" }
