param(
  [Parameter(Mandatory=$true)][string]$Model
)
$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
$configPath=".\config\story_model_config.json"
$c=Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$found=$c.candidates | Where-Object { $_.runtime_model -eq $Model }
if(-not $found){ throw "Model is not in Story candidate list: $Model" }
$c.active_model=$Model
$c.active_brain_id=$found.id
$c.status="CHAMPION_SELECTED_AFTER_STORY_BENCH"
$c | ConvertTo-Json -Depth 20 | Set-Content $configPath -Encoding UTF8
Write-Host "STORY CHAMPION: $Model" -ForegroundColor Green
Write-Host "Config updated locally: $configPath"
