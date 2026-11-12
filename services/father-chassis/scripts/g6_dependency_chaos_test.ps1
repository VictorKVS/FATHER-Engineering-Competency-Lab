param([int]$RecoveryTimeoutSeconds = 90)

$ErrorActionPreference = "Stop"

$image = "father-chassis-father-chassis:latest"
$artifactDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\artifacts"))
$summaryPath = Join-Path $artifactDir "g6_6_dependency_chaos_summary.json"
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null

function Get-FreeTcpPort {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
    try {
        $listener.Start()
        return ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port
    }
    finally {
        $listener.Stop()
    }
}

function Wait-Ready([string]$BaseUrl, [int]$TimeoutSec) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    do {
        try {
            $r = Invoke-RestMethod ($BaseUrl + "/health/ready") -TimeoutSec 3
            if ($r.ready) { return $true }
        }
        catch {}
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)
    return $false
}

function Get-Status([string]$Url) {
    try {
        return [int](Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 5).StatusCode
    }
    catch {
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            return [int]$_.Exception.Response.StatusCode
        }
        return 0
    }
}

function Run-Request([string]$BaseUrl, [string]$Text) {
    try {
        $body = @{ input = $Text } | ConvertTo-Json
        $r = Invoke-RestMethod ($BaseUrl + "/run") -Method Post -ContentType "application/json" -Body $body -TimeoutSec 120
        return [pscustomobject]@{ ok = $true; trace_id = [string]$r.trace_id; error = $null }
    }
    catch {
        $status = 0
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $status = [int]$_.Exception.Response.StatusCode
        }
        return [pscustomobject]@{ ok = $false; trace_id = $null; error = ("HTTP {0}: {1}" -f $status,$_.Exception.Message) }
    }
}

function Remove-Container([string]$Name) {
    $saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        docker rm -f $Name *> $null
    }
    finally {
        $ErrorActionPreference = $saved
    }
}

function Wait-ComposeRunning([string]$Service,[int]$TimeoutSec) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    do {
        $id = (docker compose ps -q $Service).Trim()
        if ($id) {
            $state = (docker inspect --format "{{.State.Status}}" $id).Trim()
            if ($state -eq "running") { return $true }
        }
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)
    return $false
}

Write-Host "[G6.6 1/10] Build current canonical image and validate dependency services"
docker compose build father-chassis
if ($LASTEXITCODE -ne 0) { throw "Could not build current canonical image" }

docker image inspect $image | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Canonical image missing after build" }

docker compose up -d postgres redis | Out-Null
if (-not (Wait-ComposeRunning "postgres" $RecoveryTimeoutSeconds)) { throw "PostgreSQL unavailable" }
if (-not (Wait-ComposeRunning "redis" $RecoveryTimeoutSeconds)) { throw "Redis unavailable" }

$pgId = (docker compose ps -q postgres).Trim()
$redisId = (docker compose ps -q redis).Trim()
$networkJson = docker inspect --format "{{json .NetworkSettings.Networks}}" $pgId | ConvertFrom-Json
$networkName = $networkJson.PSObject.Properties.Name | Select-Object -First 1
if (-not $networkName) { throw "Could not resolve compose network" }

$pgContainer = (docker inspect --format "{{.Name}}" $pgId).Trim().TrimStart("/")
$redisContainer = (docker inspect --format "{{.Name}}" $redisId).Trim().TrimStart("/")

$pgUser = (docker compose exec -T postgres sh -lc 'printf %s "$POSTGRES_USER"').Trim()
$pgDb = (docker compose exec -T postgres sh -lc 'printf %s "$POSTGRES_DB"').Trim()
$pgPassword = (docker compose exec -T postgres sh -lc 'printf %s "$POSTGRES_PASSWORD"').Trim()
if (-not $pgUser) { $pgUser = "father" }
if (-not $pgDb) { $pgDb = "father" }

Write-Host "[G6.6 2/10] Start isolated runtime with PostgreSQL + Redis"
$port = Get-FreeTcpPort
$base = "http://127.0.0.1:$port"
$chaosName = "father-g6-6-dependency-chaos"
Remove-Container $chaosName

$pgDsn = "postgresql://{0}:{1}@{2}:5432/{3}" -f $pgUser,$pgPassword,$pgContainer,$pgDb
$redisUrl = "redis://{0}:6379/0" -f $redisContainer
$portMap = "{0}:8080" -f $port

docker run -d --name $chaosName --network $networkName -p $portMap --add-host host.docker.internal:host-gateway -e FATHER_DATA_DIR=/app/data-chaos -e FATHER_STATE_BACKEND=postgres -e FATHER_POSTGRES_DSN=$pgDsn -e FATHER_EVENT_BUS=redis -e FATHER_REDIS_URL=$redisUrl -e FATHER_MODEL_BASE_URL=http://host.docker.internal:11434/v1 -e FATHER_MODEL_NAME=qwen2.5:7b $image uvicorn father.api_modular:app --host 0.0.0.0 --port 8080 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Could not start isolated runtime" }

if (-not (Wait-Ready $base $RecoveryTimeoutSeconds)) {
    docker logs --tail=120 $chaosName
    throw "Isolated runtime not ready"
}

$baseline = Run-Request $base "G6.6 baseline dependency chaos"
if (-not $baseline.ok) { throw ("Baseline run failed: " + $baseline.error) }

Write-Host "[G6.6 3/10] PostgreSQL outage"
docker compose stop postgres | Out-Null
Start-Sleep -Seconds 3
$pgReady = Get-Status ($base + "/health/ready")
$pgRun = Run-Request $base "G6.6 while PostgreSQL unavailable"

if ($pgReady -ne 503) { throw ("G6.6 FAIL: PostgreSQL outage not reflected by readiness: " + $pgReady) }
if ($pgRun.ok) { throw "G6.6 FAIL: request succeeded with unavailable PostgreSQL state backend" }

Write-Host "[G6.6 4/10] PostgreSQL recovery"
docker compose start postgres | Out-Null
if (-not (Wait-ComposeRunning "postgres" $RecoveryTimeoutSeconds)) { throw "PostgreSQL did not recover" }
if (-not (Wait-Ready $base $RecoveryTimeoutSeconds)) { throw "Runtime readiness did not recover after PostgreSQL" }
$pgRecovered = Run-Request $base "G6.6 after PostgreSQL recovery"
if (-not $pgRecovered.ok) { throw "Runtime did not recover after PostgreSQL" }

Write-Host "[G6.6 5/10] Redis outage"
docker compose stop redis | Out-Null
Start-Sleep -Seconds 3
$redisReady = Get-Status ($base + "/health/ready")
$redisRun = Run-Request $base "G6.6 while Redis unavailable"
$redisBlindSpot = ($redisReady -eq 200)

Write-Host "[G6.6 6/10] Redis recovery"
docker compose start redis | Out-Null
if (-not (Wait-ComposeRunning "redis" $RecoveryTimeoutSeconds)) { throw "Redis did not recover" }

$redisRecovered = $false
$deadline = (Get-Date).AddSeconds($RecoveryTimeoutSeconds)
do {
    $redisRecoveredRun = Run-Request $base "G6.6 after Redis recovery"
    if ($redisRecoveredRun.ok) {
        $redisRecovered = $true
        break
    }
    Start-Sleep -Seconds 2
} while ((Get-Date) -lt $deadline)

if (-not $redisRecovered) { throw "Runtime did not recover after Redis" }

Write-Host "[G6.6 7/10] Primary model outage with secondary fallback"
$modelPort = Get-FreeTcpPort
$modelBase = "http://127.0.0.1:$modelPort"
$modelName = "father-g6-6-model-chaos"
$modelPortMap = "{0}:8080" -f $modelPort
Remove-Container $modelName

docker run -d --name $modelName -p $modelPortMap -e FATHER_DATA_DIR=/app/data-model-chaos -e FATHER_STATE_BACKEND=sqlite -e FATHER_EVENT_BUS=memory -e FATHER_MODEL_BASE_URL=http://127.0.0.1:9/v1 -e FATHER_MODEL_NAME=g6.6-unreachable-primary $image uvicorn father.api_modular:app --host 0.0.0.0 --port 8080 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Could not start model-chaos runtime" }

Start-Sleep -Seconds 3
$modelReady = Get-Status ($modelBase + "/health/ready")
$modelRun = Run-Request $modelBase "G6.6 model-router fallback proof"
if (-not $modelRun.ok) {
    docker logs --tail=120 $modelName
    throw "G6.6 FAIL: model fallback failed"
}

Write-Host "[G6.6 8/10] Final post-chaos request and audit"
$finalRun = Run-Request $base "G6.6 final post-chaos request"
if (-not $finalRun.ok) { throw "Final post-chaos run failed" }
$audit = Invoke-RestMethod ($base + "/audit/" + $finalRun.trace_id) -TimeoutSec 10
if (@($audit.events).Count -lt 2) { throw "Final post-chaos audit incomplete" }

Write-Host "[G6.6 9/10] Evaluate architecture findings"
$findings = New-Object System.Collections.Generic.List[string]
if ($redisBlindSpot) { $findings.Add("ACTIVE_REDIS_EVENT_BUS_NOT_REFLECTED_IN_READINESS") }
if ((-not $redisRun.ok) -and $redisBlindSpot) { $findings.Add("REDIS_REQUEST_FAILURE_WITH_FALSE_READY_STATUS") }
$modelMismatch = (($modelReady -ne 200) -and $modelRun.ok)

Write-Host "[G6.6 10/10] Produce qualification evidence"
$result = [ordered]@{
    qualification = "G6.6_DEPENDENCY_CHAOS"
    passed = ($findings.Count -eq 0)
    baseline_trace_id = $baseline.trace_id
    postgres = [ordered]@{
        readiness_status_during_outage = $pgReady
        request_failed_during_outage = (-not $pgRun.ok)
        recovered = $pgRecovered.ok
        recovered_trace_id = $pgRecovered.trace_id
    }
    redis = [ordered]@{
        readiness_status_during_outage = $redisReady
        request_failed_during_outage = (-not $redisRun.ok)
        readiness_blind_spot = $redisBlindSpot
        recovered = $redisRecovered
        recovered_trace_id = $redisRecoveredRun.trace_id
    }
    model_provider = [ordered]@{
        primary_endpoint_intentionally_unreachable = $true
        readiness_status = $modelReady
        fallback_run_succeeded = $modelRun.ok
        fallback_trace_id = $modelRun.trace_id
        readiness_vs_fallback_mismatch = $modelMismatch
    }
    final_post_chaos_trace_id = $finalRun.trace_id
    final_post_chaos_audit_event_count = @($audit.events).Count
    blocking_findings = @($findings)
}

$result | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 $summaryPath
Remove-Container $chaosName
Remove-Container $modelName

if ($findings.Count -gt 0) {
    Write-Host ""
    Write-Host "G6.6 DEPENDENCY CHAOS QUALIFICATION: FAIL"
    $result | ConvertTo-Json -Depth 12
    throw ("G6.6 blocking findings: " + ($findings -join ", "))
}

Write-Host ""
Write-Host "G6.6 DEPENDENCY CHAOS QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 12
