$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"

Write-Host "[1/6] Liveness"
$live = Invoke-RestMethod "$base/health/live"
if (-not $live.live) { throw "Liveness failed" }

Write-Host "[2/6] Readiness"
$ready = Invoke-RestMethod "$base/health/ready"
if (-not $ready.ready) { throw "Readiness failed" }

Write-Host "[3/6] Ingest"
$body = @{
    source = "qualification"
    text = "FATHER Chassis is a reusable platform core for agent systems. This is qualification evidence."
} | ConvertTo-Json
$ing = Invoke-RestMethod "$base/ingest" -Method Post -ContentType "application/json" -Body $body
if ($ing.chunks -lt 1) { throw "Ingest failed" }

Write-Host "[4/6] Run"
$runBody = @{ input = "What is FATHER Chassis?" } | ConvertTo-Json
$run = Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $runBody
if ([string]::IsNullOrWhiteSpace($run.trace_id)) { throw "Run trace_id missing" }

Write-Host "[5/6] Audit"
$audit = Invoke-RestMethod "$base/audit/$($run.trace_id)"
if ($audit.events.Count -lt 2) { throw "Audit trail incomplete" }

Write-Host "[6/6] Emergency stop"
Invoke-RestMethod "$base/control/stop" -Method Post | Out-Null
try {
    Invoke-RestMethod "$base/health/ready" -TimeoutSec 3 | Out-Null
    throw "Readiness should fail while emergency stop is active"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -ne 503) { throw }
}
Invoke-RestMethod "$base/control/resume" -Method Post | Out-Null

Write-Host "`nSMOKE TEST: PASS"
