$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"

Write-Host "[1/5] Ingest persistence marker"
$body = @{
    source = "recovery-test"
    text = "Persistent marker: FATHER-RECOVERY-0.7"
} | ConvertTo-Json
Invoke-RestMethod "$base/ingest" -Method Post -ContentType "application/json" -Body $body | Out-Null

Write-Host "[2/5] Restart API container"
docker compose restart father-chassis
Start-Sleep -Seconds 5

Write-Host "[3/5] Wait for readiness"
$deadline = (Get-Date).AddMinutes(2)
$r = $null
do {
    try {
        $r = Invoke-RestMethod "$base/health/ready" -TimeoutSec 3
        if ($r.ready) { break }
    } catch {}
    Start-Sleep -Seconds 2
} while ((Get-Date) -lt $deadline)
if ($null -eq $r -or -not $r.ready) { throw "Service did not recover" }

Write-Host "[4/5] Query persisted knowledge"
$q = @{ input = "FATHER-RECOVERY-0.7" } | ConvertTo-Json
$res = Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $q
if (-not $res.evidence -or $res.evidence.Count -lt 1) { throw "Persistent knowledge not recovered" }

Write-Host "[5/5] Containers"
docker compose ps

Write-Host "`nRECOVERY TEST: PASS"
