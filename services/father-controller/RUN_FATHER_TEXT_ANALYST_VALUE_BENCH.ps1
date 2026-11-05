param(
  [double]$PricePerKWh = 0,
  [string]$Currency = "RUB",
  [int]$Questions = 12
)
$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

python -c "import psutil" 2>$null
if($LASTEXITCODE -ne 0){
  python -m pip install psutil
  if($LASTEXITCODE -ne 0){ throw "Cannot install psutil" }
}

$models = @(
  "qwen2.5:3b",
  "qwen2.5:7b",
  "qwen2.5-coder:7b-instruct-q4_K_M",
  "llama3.2:1b"
)

Write-Host "=== FATHER TEXT ANALYST VALUE BENCH MVP-01 ===" -ForegroundColor Cyan
Write-Host "Models: $($models.Count) | Questions/model: $Questions" -ForegroundColor Cyan

foreach($m in $models){
  Write-Host ""
  Write-Host "=== VALUE MODEL: $m ===" -ForegroundColor Yellow
  python .\run_resource_energy_meter.py --label $m --price-per-kwh $PricePerKWh --currency $Currency --task-count $Questions -- python .\run_text_analyst_value_workload.py --model $m --questions $Questions
  if($LASTEXITCODE -ne 0){ throw "Value workload failed for $m" }
}

python .\build_text_analyst_value_matrix.py
if($LASTEXITCODE -ne 0){ throw "Value matrix aggregation failed" }

Write-Host "=== VALUE BENCH COMPLETE ===" -ForegroundColor Green
Write-Host "Evidence: evidence/text_analyst_value/value_matrix_latest.json" -ForegroundColor Green
