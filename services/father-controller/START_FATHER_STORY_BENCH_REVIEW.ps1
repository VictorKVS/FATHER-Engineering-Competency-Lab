$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
if(-not (Test-Path ".\evidence\story_model_bench_latest.json")){
  throw "Run .\RUN_FATHER_STORY_BENCH.ps1 first"
}
$port=8092
if(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue){
  Start-Process "http://127.0.0.1:$port"; exit 0
}
Start-Process python -ArgumentList ".\story_bench_review_server.py" -WorkingDirectory $PSScriptRoot
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:$port"
Write-Host "Story Bench Review: http://127.0.0.1:$port" -ForegroundColor Green
