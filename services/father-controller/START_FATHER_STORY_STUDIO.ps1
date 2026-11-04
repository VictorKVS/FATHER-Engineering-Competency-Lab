$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
$port=8091
if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
  Write-Host "Story Studio already running: http://127.0.0.1:$port" -ForegroundColor Yellow
  Start-Process "http://127.0.0.1:$port"
  exit 0
}
Write-Host "Starting FATHER Story Studio..." -ForegroundColor Cyan
Start-Process python -ArgumentList ".\story_studio_server.py" -WorkingDirectory $PSScriptRoot
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:$port"
Write-Host "Story Studio: http://127.0.0.1:$port" -ForegroundColor Green
