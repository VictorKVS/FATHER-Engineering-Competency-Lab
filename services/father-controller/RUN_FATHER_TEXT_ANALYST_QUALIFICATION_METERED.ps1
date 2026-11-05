param(
  [double]$PricePerKWh = 0,
  [string]$Currency = "RUB"
)
$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

Write-Host "=== FATHER TEXT ANALYST QUALIFICATION / METERED ===" -ForegroundColor Cyan
python -c "import psutil" 2>$null
if($LASTEXITCODE -ne 0){
  Write-Host "Installing psutil for CPU utilization/power estimate..." -ForegroundColor Yellow
  python -m pip install psutil
  if($LASTEXITCODE -ne 0){ throw "Cannot install psutil" }
}
if($PricePerKWh -le 0){
  Write-Host "PricePerKWh=0: energy will be measured/estimated, money cost will be N/A." -ForegroundColor Yellow
  Write-Host "Example: .\RUN_FATHER_TEXT_ANALYST_QUALIFICATION_METERED.ps1 -PricePerKWh 8.50 -Currency RUB" -ForegroundColor Yellow
}

python .\run_resource_energy_meter.py --price-per-kwh $PricePerKWh --currency $Currency --task-count 810 -- powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\RUN_FATHER_TEXT_ANALYST_QUALIFICATION.ps1
if($LASTEXITCODE -ne 0){ throw "Metered qualification run failed with code $LASTEXITCODE" }
