$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"

$controlWorkers = 16
$controlRequestsPerWorker = 50
$runtimeWorkers = 4
$runtimeRequestsPerWorker = 2

function Get-Percentile([double[]]$values, [double]$percentile) {
    if (-not $values -or $values.Count -eq 0) { return $null }
    $sorted = @($values | Sort-Object)
    $index = [Math]::Ceiling(($percentile / 100.0) * $sorted.Count) - 1
    if ($index -lt 0) { $index = 0 }
    if ($index -ge $sorted.Count) { $index = $sorted.Count - 1 }
    return [Math]::Round([double]$sorted[$index], 2)
}

function Assert-CanonicalModular {
    $root = Invoke-RestMethod "$base/" -TimeoutSec 5
    if ($root.service -ne "FATHER Chassis Modular") {
        throw "G6 load test requires canonical modular runtime on 8080"
    }
}

Write-Host "[G6.1 1/7] Validate canonical modular runtime"
Assert-CanonicalModular

Write-Host "[G6.1 2/7] Verify readiness before load"
$ready = Invoke-RestMethod "$base/health/ready" -TimeoutSec 5
if (-not $ready.ready) { throw "canonical runtime is not ready before load" }

Write-Host "[G6.1 3/7] Run control-plane concurrent load: $controlWorkers workers x $controlRequestsPerWorker requests"
$controlJobs = @()
for ($worker = 1; $worker -le $controlWorkers; $worker++) {
    $controlJobs += Start-Job -ArgumentList $base, $worker, $controlRequestsPerWorker -ScriptBlock {
        param($baseUrl, $workerId, $requestCount)
        $rows = @()
        for ($i = 1; $i -le $requestCount; $i++) {
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $ok = $false
            $errorText = $null
            try {
                $response = Invoke-RestMethod "$baseUrl/health/live" -TimeoutSec 10
                $ok = [bool]$response.live
            } catch {
                $errorText = $_.Exception.Message
            }
            $sw.Stop()
            $rows += [pscustomobject]@{
                Worker = $workerId
                Request = $i
                Ok = $ok
                ElapsedMs = [double]$sw.Elapsed.TotalMilliseconds
                Error = $errorText
            }
        }
        $rows
    }
}

$controlJobs | Wait-Job | Out-Null
$controlRows = @($controlJobs | Receive-Job)
$controlJobs | Remove-Job -Force

$controlTotal = $controlRows.Count
$controlPassed = @($controlRows | Where-Object { $_.Ok }).Count
$controlFailed = $controlTotal - $controlPassed
$controlLatency = [double[]]@($controlRows | Where-Object { $_.Ok } | ForEach-Object { $_.ElapsedMs })
$controlP50 = Get-Percentile $controlLatency 50
$controlP95 = Get-Percentile $controlLatency 95
$controlP99 = Get-Percentile $controlLatency 99
$controlMax = if ($controlLatency.Count) { [Math]::Round(($controlLatency | Measure-Object -Maximum).Maximum, 2) } else { $null }

if ($controlTotal -ne ($controlWorkers * $controlRequestsPerWorker)) {
    throw "control-plane result count mismatch: expected $($controlWorkers * $controlRequestsPerWorker), got $controlTotal"
}
if ($controlFailed -ne 0) {
    $controlRows | Where-Object { -not $_.Ok } | Select-Object -First 10 | Format-Table -AutoSize
    throw "control-plane concurrent load has $controlFailed failed requests"
}

Write-Host "[G6.1 4/7] Prepare evidence for real inference concurrency"
$evidenceText = @{
    source = "g6-concurrent-load"
    text = "FATHER Chassis G6 concurrent load qualification verifies canonical modular runtime, unique execution traces, evidence-backed model inference and audit continuity under simultaneous requests."
} | ConvertTo-Json
Invoke-RestMethod "$base/ingest" -Method Post -ContentType "application/json" -Body $evidenceText -TimeoutSec 20 | Out-Null

Write-Host "[G6.1 5/7] Run real inference concurrency: $runtimeWorkers workers x $runtimeRequestsPerWorker requests"
$runtimeJobs = @()
for ($worker = 1; $worker -le $runtimeWorkers; $worker++) {
    $runtimeJobs += Start-Job -ArgumentList $base, $worker, $runtimeRequestsPerWorker -ScriptBlock {
        param($baseUrl, $workerId, $requestCount)
        $rows = @()
        for ($i = 1; $i -le $requestCount; $i++) {
            $payload = @{
                input = "What does the FATHER G6 concurrent load qualification verify?"
            } | ConvertTo-Json

            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $ok = $false
            $traceId = $null
            $evidenceCount = 0
            $errorText = $null
            try {
                $response = Invoke-RestMethod "$baseUrl/run" -Method Post -ContentType "application/json" -Body $payload -TimeoutSec 180
                $traceId = [string]$response.trace_id
                $evidenceCount = @($response.evidence).Count
                $ok = (
                    -not [string]::IsNullOrWhiteSpace($traceId) -and
                    -not [string]::IsNullOrWhiteSpace([string]$response.output) -and
                    $evidenceCount -gt 0
                )
            } catch {
                $errorText = $_.Exception.Message
            }
            $sw.Stop()
            $rows += [pscustomobject]@{
                Worker = $workerId
                Request = $i
                Ok = $ok
                TraceId = $traceId
                EvidenceCount = $evidenceCount
                ElapsedMs = [double]$sw.Elapsed.TotalMilliseconds
                Error = $errorText
            }
        }
        $rows
    }
}

$runtimeJobs | Wait-Job | Out-Null
$runtimeRows = @($runtimeJobs | Receive-Job)
$runtimeJobs | Remove-Job -Force

$runtimeTotal = $runtimeRows.Count
$runtimePassed = @($runtimeRows | Where-Object { $_.Ok }).Count
$runtimeFailed = $runtimeTotal - $runtimePassed
$runtimeLatency = [double[]]@($runtimeRows | Where-Object { $_.Ok } | ForEach-Object { $_.ElapsedMs })
$runtimeP50 = Get-Percentile $runtimeLatency 50
$runtimeP95 = Get-Percentile $runtimeLatency 95
$runtimeMax = if ($runtimeLatency.Count) { [Math]::Round(($runtimeLatency | Measure-Object -Maximum).Maximum, 2) } else { $null }

if ($runtimeTotal -ne ($runtimeWorkers * $runtimeRequestsPerWorker)) {
    throw "runtime result count mismatch: expected $($runtimeWorkers * $runtimeRequestsPerWorker), got $runtimeTotal"
}
if ($runtimeFailed -ne 0) {
    $runtimeRows | Where-Object { -not $_.Ok } | Format-Table -AutoSize
    throw "real inference concurrent load has $runtimeFailed failed requests"
}

$traceIds = @($runtimeRows | ForEach-Object { $_.TraceId } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$uniqueTraceIds = @($traceIds | Sort-Object -Unique)
if ($uniqueTraceIds.Count -ne $runtimeTotal) {
    throw "trace uniqueness failed: expected $runtimeTotal unique traces, got $($uniqueTraceIds.Count)"
}

Write-Host "[G6.1 6/7] Validate audit continuity for every concurrent inference"
foreach ($traceId in $uniqueTraceIds) {
    $audit = Invoke-RestMethod "$base/audit/$traceId" -TimeoutSec 10
    $eventTypes = @($audit.events | ForEach-Object { $_.type })
    if ($eventTypes -notcontains "request.received") { throw "audit missing request.received for trace $traceId" }
    if ($eventTypes -notcontains "model.completed") { throw "audit missing model.completed for trace $traceId" }
    if ($eventTypes -notcontains "request.completed") { throw "audit missing request.completed for trace $traceId" }
}

Write-Host "[G6.1 7/7] Verify runtime readiness after load"
$after = Invoke-RestMethod "$base/health/ready" -TimeoutSec 5
if (-not $after.ready) { throw "canonical runtime is not ready after concurrent load" }

$result = [ordered]@{
    qualification = "G6.1_CONCURRENT_LOAD"
    passed = $true
    canonical_endpoint = $base
    control_plane = [ordered]@{
        workers = $controlWorkers
        requests_per_worker = $controlRequestsPerWorker
        total_requests = $controlTotal
        failed_requests = $controlFailed
        p50_ms = $controlP50
        p95_ms = $controlP95
        p99_ms = $controlP99
        max_ms = $controlMax
    }
    real_inference = [ordered]@{
        workers = $runtimeWorkers
        requests_per_worker = $runtimeRequestsPerWorker
        total_requests = $runtimeTotal
        failed_requests = $runtimeFailed
        unique_trace_ids = $uniqueTraceIds.Count
        p50_ms = $runtimeP50
        p95_ms = $runtimeP95
        max_ms = $runtimeMax
    }
    audit_verified_traces = $uniqueTraceIds.Count
    runtime_ready_after_load = [bool]$after.ready
}

Write-Host ""
Write-Host "G6.1 CONCURRENT LOAD QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 10
