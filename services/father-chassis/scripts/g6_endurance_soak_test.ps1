param(
    [int]$DurationMinutes = 120,
    [int]$ProbeIntervalSeconds = 10,
    [int]$RealRunIntervalSeconds = 300
)

$ErrorActionPreference = "Stop"

$base = "http://localhost:8080"
$service = "father-chassis"
$artifactDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\artifacts"))
$summaryPath = Join-Path $artifactDir "g6_5_endurance_soak_summary.json"
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null

function Percentile([double[]]$values, [double]$p) {
    if (-not $values -or $values.Count -eq 0) { return 0.0 }
    $sorted = @($values | Sort-Object)
    $index = [Math]::Ceiling(($p / 100.0) * $sorted.Count) - 1
    if ($index -lt 0) { $index = 0 }
    if ($index -ge $sorted.Count) { $index = $sorted.Count - 1 }
    return [double]$sorted[$index]
}

function Get-ContainerStats {
    $containerId = (docker compose ps -q $service).Trim()
    if ([string]::IsNullOrWhiteSpace($containerId)) {
        throw "Could not resolve running container ID for $service"
    }
    $raw = docker stats $containerId --no-stream --format "{{json .}}"
    if ($LASTEXITCODE -ne 0) { throw "Could not read Docker stats for $service ($containerId)" }
    return $raw | ConvertFrom-Json
}

Write-Host "[G6.5 1/7] Validate canonical runtime"
$root = Invoke-RestMethod "$base/"
if ($root.service -ne "FATHER Chassis Modular") { throw "Canonical modular runtime is not active on 8080" }
$ready = Invoke-RestMethod "$base/health/ready"
if (-not $ready.ready) { throw "Canonical runtime is not ready" }

Write-Host "[G6.5 2/7] Establish baseline resource usage"
$baselineStats = Get-ContainerStats

Write-Host "[G6.5 3/7] Start endurance workload"
$deadline = (Get-Date).AddMinutes($DurationMinutes)
$nextRealRun = Get-Date
$probeLatencies = New-Object System.Collections.Generic.List[double]
$runLatencies = New-Object System.Collections.Generic.List[double]
$probeFailures = 0
$runFailures = 0
$realRuns = 0
$auditVerified = 0
$traceIds = New-Object System.Collections.Generic.HashSet[string]
$memorySamples = New-Object System.Collections.Generic.List[string]
$cpuSamples = New-Object System.Collections.Generic.List[string]

while ((Get-Date) -lt $deadline) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $h = Invoke-RestMethod "$base/health/ready" -TimeoutSec 5
        if (-not $h.ready) { throw "not ready" }
        $sw.Stop()
        $probeLatencies.Add($sw.Elapsed.TotalMilliseconds)
    }
    catch {
        $sw.Stop()
        $probeFailures++
    }

    $stats = Get-ContainerStats
    $memorySamples.Add([string]$stats.MemUsage)
    $cpuSamples.Add([string]$stats.CPUPerc)

    if ((Get-Date) -ge $nextRealRun) {
        $runSw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $body = @{ input = "G6.5 endurance qualification: explain the role of FATHER Chassis shared runtime capabilities." } | ConvertTo-Json
            $run = Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 120
            $runSw.Stop()
            $runLatencies.Add($runSw.Elapsed.TotalMilliseconds)
            $realRuns++

            if ([string]::IsNullOrWhiteSpace($run.trace_id)) { throw "trace missing" }
            [void]$traceIds.Add([string]$run.trace_id)

            $audit = Invoke-RestMethod "$base/audit/$($run.trace_id)" -TimeoutSec 10
            if (@($audit.events).Count -lt 2) { throw "audit incomplete" }
            $auditVerified++
        }
        catch {
            if ($runSw.IsRunning) { $runSw.Stop() }
            $runFailures++
        }
        $nextRealRun = (Get-Date).AddSeconds($RealRunIntervalSeconds)
    }

    Start-Sleep -Seconds $ProbeIntervalSeconds
}

Write-Host "[G6.5 4/7] Capture final resource usage"
$finalStats = Get-ContainerStats

Write-Host "[G6.5 5/7] Validate runtime after soak"
$finalReady = Invoke-RestMethod "$base/health/ready"
if (-not $finalReady.ready) { throw "Runtime not ready after endurance test" }

Write-Host "[G6.5 6/7] Apply endurance acceptance criteria"
$totalProbes = $probeLatencies.Count + $probeFailures
if ($totalProbes -lt 1) { throw "No readiness probes executed" }

$probeFailureRate = [double]$probeFailures / [double]$totalProbes
$runTotal = $realRuns + $runFailures
$runFailureRate = if ($runTotal -gt 0) { [double]$runFailures / [double]$runTotal } else { 1.0 }

if ($probeFailureRate -gt 0.01) {
    throw "G6.5 FAIL: readiness probe failure rate exceeded 1%: $probeFailureRate"
}
if ($runFailureRate -gt 0.05) {
    throw "G6.5 FAIL: real run failure rate exceeded 5%: $runFailureRate"
}
if ($realRuns -lt 1) {
    throw "G6.5 FAIL: no successful real runs were executed"
}
if ($auditVerified -ne $realRuns) {
    throw "G6.5 FAIL: not every successful real run has verified audit evidence"
}

Write-Host "[G6.5 7/7] Produce qualification evidence"
$result = [ordered]@{
    qualification = "G6.5_ENDURANCE_SOAK"
    passed = $true
    duration_minutes = $DurationMinutes
    probe_interval_seconds = $ProbeIntervalSeconds
    real_run_interval_seconds = $RealRunIntervalSeconds
    total_probes = $totalProbes
    probe_failures = $probeFailures
    probe_failure_rate = $probeFailureRate
    probe_p50_ms = [Math]::Round((Percentile $probeLatencies.ToArray() 50), 2)
    probe_p95_ms = [Math]::Round((Percentile $probeLatencies.ToArray() 95), 2)
    probe_p99_ms = [Math]::Round((Percentile $probeLatencies.ToArray() 99), 2)
    successful_real_runs = $realRuns
    failed_real_runs = $runFailures
    run_failure_rate = $runFailureRate
    run_p50_ms = [Math]::Round((Percentile $runLatencies.ToArray() 50), 2)
    run_p95_ms = [Math]::Round((Percentile $runLatencies.ToArray() 95), 2)
    unique_trace_ids = $traceIds.Count
    audit_verified_runs = $auditVerified
    baseline_memory = [string]$baselineStats.MemUsage
    final_memory = [string]$finalStats.MemUsage
    baseline_cpu = [string]$baselineStats.CPUPerc
    final_cpu = [string]$finalStats.CPUPerc
    runtime_ready_after_soak = $true
}
$result | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $summaryPath

Write-Host ""
Write-Host "G6.5 ENDURANCE / SOAK QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 10
