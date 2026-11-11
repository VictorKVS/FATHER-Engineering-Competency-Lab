$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"
$healthSamples = New-Object System.Collections.Generic.List[double]
$runSamples = New-Object System.Collections.Generic.List[double]
$failures = 0

function Percentile([double[]]$values, [double]$p) {
    if (-not $values -or $values.Count -eq 0) { return 0 }
    $sorted = $values | Sort-Object
    $idx = [Math]::Ceiling(($p / 100.0) * $sorted.Count) - 1
    if ($idx -lt 0) { $idx = 0 }
    return [Math]::Round([double]$sorted[$idx], 2)
}

Write-Host "[G6.1] 200 liveness requests"
for ($i=1; $i -le 200; $i++) {
    $sw=[Diagnostics.Stopwatch]::StartNew()
    try {
        $r=Invoke-RestMethod "$base/health/live" -TimeoutSec 5
        if (-not $r.live) { throw "live=false" }
    } catch {
        $failures++
    } finally {
        $sw.Stop()
        $healthSamples.Add($sw.Elapsed.TotalMilliseconds)
    }
}

Write-Host "[G6.1] 50 grounded run requests"
for ($i=1; $i -le 50; $i++) {
    $body=@{input="FATHER industrial load qualification request $i"} | ConvertTo-Json
    $sw=[Diagnostics.Stopwatch]::StartNew()
    try {
        $r=Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 10
        if ([string]::IsNullOrWhiteSpace($r.trace_id)) { throw "trace missing" }
    } catch {
        $failures++
    } finally {
        $sw.Stop()
        $runSamples.Add($sw.Elapsed.TotalMilliseconds)
    }
}

$healthP95=Percentile $healthSamples.ToArray() 95
$runP95=Percentile $runSamples.ToArray() 95
$result=[ordered]@{
    gate="G6.1_LOAD"
    health_requests=200
    run_requests=50
    failures=$failures
    health_p95_ms=$healthP95
    run_p95_ms=$runP95
    thresholds=@{failures=0; health_p95_ms=500; run_p95_ms=2000}
    passed=($failures -eq 0 -and $healthP95 -le 500 -and $runP95 -le 2000)
}
$result | ConvertTo-Json -Depth 10 | Set-Content ".\artifacts\g6_load.json"
$result | ConvertTo-Json -Depth 10
if (-not $result.passed) { Write-Host "G6.1 LOAD: FAIL"; exit 1 }
Write-Host "G6.1 LOAD: PASS"
