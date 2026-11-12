$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"
$service = "father-chassis"

function Wait-Ready([int]$timeoutSeconds = 120) {
    $deadline = (Get-Date).AddSeconds($timeoutSeconds)
    do {
        try {
            $r = Invoke-RestMethod "$base/health/ready" -TimeoutSec 3
            if ($r.ready) { return $true }
        } catch {}
        Start-Sleep -Seconds 1
    } while ((Get-Date) -lt $deadline)
    return $false
}

function Assert-ModularIdentity {
    $root = Invoke-RestMethod "$base/" -TimeoutSec 5
    if ($root.service -ne "FATHER Chassis Modular") {
        throw "G6.2 requires canonical modular runtime on 8080"
    }
}

Write-Host "[G6.2 1/8] Validate canonical modular runtime"
Assert-ModularIdentity
if (-not (Wait-Ready 20)) { throw "runtime not ready before chaos" }

Write-Host "[G6.2 2/8] Start continuous probe load in background"
$probeJob = Start-Job -ArgumentList $base -ScriptBlock {
    param($baseUrl)
    $rows = @()
    $deadline = (Get-Date).AddSeconds(35)
    $i = 0
    while ((Get-Date) -lt $deadline) {
        $i++
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $ok = $false
        $status = $null
        $errorText = $null
        try {
            $r = Invoke-WebRequest "$baseUrl/health/live" -UseBasicParsing -TimeoutSec 3
            $status = [int]$r.StatusCode
            $ok = ($status -eq 200)
        } catch {
            try { $status = [int]$_.Exception.Response.StatusCode.value__ } catch {}
            $errorText = $_.Exception.Message
        }
        $sw.Stop()
        $rows += [pscustomobject]@{
            Index = $i
            Time = (Get-Date).ToString("o")
            Ok = $ok
            Status = $status
            ElapsedMs = [Math]::Round($sw.Elapsed.TotalMilliseconds, 2)
            Error = $errorText
        }
        Start-Sleep -Milliseconds 250
    }
    $rows
}

Start-Sleep -Seconds 3

Write-Host "[G6.2 3/8] Inject failure: stop canonical modular container"
$failureStart = Get-Date
docker compose stop $service
if ($LASTEXITCODE -ne 0) { throw "failed to inject container stop chaos" }

Start-Sleep -Seconds 4

Write-Host "[G6.2 4/8] Restore canonical modular container"
docker compose up -d --no-build $service
if ($LASTEXITCODE -ne 0) { throw "failed to restart canonical modular container" }

$recoveryStart = Get-Date
if (-not (Wait-Ready 120)) {
    docker compose logs --tail=200 $service
    throw "runtime did not recover readiness after chaos"
}
$recoveredAt = Get-Date
$recoverySeconds = [Math]::Round(($recoveredAt - $recoveryStart).TotalSeconds, 2)

Write-Host "[G6.2 5/8] Wait for background probe completion and analyze outage window"
$probeJob | Wait-Job | Out-Null
$probeRows = @($probeJob | Receive-Job)
$probeJob | Remove-Job -Force

$totalProbes = $probeRows.Count
$successfulProbes = @($probeRows | Where-Object { $_.Ok }).Count
$failedProbes = $totalProbes - $successfulProbes

if ($totalProbes -lt 20) { throw "insufficient probe samples collected" }
if ($failedProbes -lt 1) { throw "chaos injection produced no observable outage; test is not proving failure handling" }
if ($successfulProbes -lt 1) { throw "no successful probes observed before/after chaos" }

$successAfterRecovery = @(
    $probeRows | Where-Object {
        $_.Ok -and ([datetime]$_.Time -ge $recoveredAt)
    }
).Count
if ($successAfterRecovery -lt 1) {
    throw "no successful background probes observed after recovery"
}

Write-Host "[G6.2 6/8] Verify evidence-backed inference after recovery"
$ingestBody = @{
    source = "g6-chaos-recovery"
    text = "FATHER G6.2 proves that the canonical modular runtime can recover after a forced container stop and continue evidence-backed execution with audit continuity."
} | ConvertTo-Json
Invoke-RestMethod "$base/ingest" -Method Post -ContentType "application/json" -Body $ingestBody -TimeoutSec 20 | Out-Null

$runBody = @{
    input = "What does FATHER G6.2 prove after chaos recovery?"
} | ConvertTo-Json
$run = Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $runBody -TimeoutSec 180
if ([string]::IsNullOrWhiteSpace($run.trace_id)) { throw "post-chaos trace_id missing" }
if ([string]::IsNullOrWhiteSpace($run.output)) { throw "post-chaos output missing" }
if (@($run.evidence).Count -lt 1) { throw "post-chaos evidence missing" }

Write-Host "[G6.2 7/8] Verify post-chaos audit continuity"
$audit = Invoke-RestMethod "$base/audit/$($run.trace_id)" -TimeoutSec 10
$types = @($audit.events | ForEach-Object { $_.type })
foreach ($required in @("request.received", "rag.completed", "model.completed", "policy.decision", "tool.completed", "request.completed")) {
    if ($types -notcontains $required) {
        throw "post-chaos audit missing $required"
    }
}

Write-Host "[G6.2 8/8] Verify canonical identity and readiness after chaos"
Assert-ModularIdentity
$ready = Invoke-RestMethod "$base/health/ready" -TimeoutSec 5
if (-not $ready.ready) { throw "runtime not ready at end of G6.2" }

$result = [ordered]@{
    qualification = "G6.2_CONCURRENT_CHAOS_RECOVERY"
    passed = $true
    canonical_endpoint = $base
    failure_injection = "docker compose stop father-chassis"
    total_background_probes = $totalProbes
    successful_background_probes = $successfulProbes
    failed_background_probes = $failedProbes
    observable_outage = ($failedProbes -gt 0)
    recovery_to_ready_seconds = $recoverySeconds
    post_recovery_successful_probes = $successAfterRecovery
    post_chaos_trace_id = $run.trace_id
    post_chaos_evidence_count = @($run.evidence).Count
    post_chaos_audit_event_count = @($audit.events).Count
    runtime_ready_after_chaos = [bool]$ready.ready
}

Write-Host ""
Write-Host "G6.2 CONCURRENT CHAOS RECOVERY QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 10
