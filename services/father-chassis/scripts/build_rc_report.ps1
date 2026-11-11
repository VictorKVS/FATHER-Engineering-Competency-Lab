$ErrorActionPreference = "Stop"
$report = @{
  release = "FATHER FACTORY 1.0 RC1"
  generated_at = (Get-Date).ToString("o")
  machine = $env:COMPUTERNAME
  user = $env:USERNAME
  checks = @()
}

function Add-Check($name, $passed, $details) {
  $report.checks += @{ name=$name; passed=$passed; details=$details }
}

try {
  $live = Invoke-RestMethod "http://localhost:8080/health/live"
  Add-Check "liveness" ([bool]$live.live) $live
} catch { Add-Check "liveness" $false @{error=$_.Exception.Message} }

try {
  $ready = Invoke-RestMethod "http://localhost:8080/health/ready"
  Add-Check "readiness" ([bool]$ready.ready) $ready
} catch { Add-Check "readiness" $false @{error=$_.Exception.Message} }

try {
  $models = Invoke-RestMethod "http://localhost:8080/models"
  Add-Check "models" ($models.models.Count -ge 1) $models
} catch { Add-Check "models" $false @{error=$_.Exception.Message} }

$report.passed = -not ($report.checks | Where-Object { -not $_.passed })
$report | ConvertTo-Json -Depth 12 | Set-Content ".\artifacts\factory_1_0_rc_machine_report.json" -Encoding UTF8
Write-Host "RC machine report written to artifacts\factory_1_0_rc_machine_report.json"
