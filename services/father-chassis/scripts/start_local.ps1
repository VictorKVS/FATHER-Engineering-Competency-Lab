$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[INFO] Created .env from .env.example"
}

Write-Host "[INFO] Building and starting FATHER Chassis..."
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] docker compose up failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "[INFO] Waiting for API readiness..."
$deadline = (Get-Date).AddMinutes(3)
do {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-RestMethod -Uri "http://localhost:8080/health/ready" -TimeoutSec 3
        if ($r.ready -eq $true) {
            Write-Host "[PASS] FATHER Chassis ready"
            exit 0
        }
    } catch {}
} while ((Get-Date) -lt $deadline)

Write-Host "[FAIL] FATHER Chassis did not become ready"
docker compose ps
docker compose logs --tail=200 father-chassis
exit 1
