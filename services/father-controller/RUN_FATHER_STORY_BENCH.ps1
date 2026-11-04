$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER STORY MODEL BENCH ===" -ForegroundColor Cyan

& .TEST_FATHER_OLLAMA.ps1
if ($LASTEXITCODE -ne 0) {
  Write-Host "Ollama preflight failed. Attempting one recovery..." -ForegroundColor Yellow
  & .TEST_FATHER_OLLAMA.ps1 -Recover
  if ($LASTEXITCODE -ne 0) { throw "Ollama preflight/recovery failed" }
}

python .un_story_model_bench.py
if($LASTEXITCODE -ne 0){throw "Story model bench failed"}
Write-Host "Report: evidencestory_model_bench_latest.json" -ForegroundColor Green
Write-Host "Next: .START_FATHER_STORY_BENCH_REVIEW.ps1" -ForegroundColor Cyan
