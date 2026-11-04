param(
    [int]$Port = 8090
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "Starting FATHER Design Studio on http://127.0.0.1:$Port" -ForegroundColor Cyan
    Start-Process -FilePath "python" -ArgumentList ".\design_studio_server.py" -WorkingDirectory $Here
    Start-Sleep -Seconds 2
} else {
    Write-Host "FATHER Design Studio is already listening on port $Port" -ForegroundColor Yellow
}

Start-Process "http://127.0.0.1:$Port"
Write-Host "FATHER Design Studio opened in browser." -ForegroundColor Green
