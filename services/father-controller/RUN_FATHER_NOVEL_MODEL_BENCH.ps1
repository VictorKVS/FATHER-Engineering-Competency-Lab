$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER NOVEL RAG + KB MODEL BENCH ===" -ForegroundColor Cyan

& ./TEST_FATHER_OLLAMA.ps1
if($LASTEXITCODE -ne 0){ throw "Ollama preflight failed" }

$novel = Join-Path $PSScriptRoot "novel_benchmark/input/novel.txt"
if(-not (Test-Path $novel)){
  throw "Novel not found: $novel . Put one UTF-8 novel into novel_benchmark/input/novel.txt"
}

python ./run_novel_model_bench.py $novel
if($LASTEXITCODE -ne 0){ throw "Novel model bench failed" }

Write-Host "=== NOVEL RAG + KB BENCH COMPLETE ===" -ForegroundColor Green
Write-Host "Evidence: evidence/novel_model_bench/novel_model_bench_latest.json"
Write-Host "Comparison: evidence/novel_model_bench/novel_model_comparison.json"
