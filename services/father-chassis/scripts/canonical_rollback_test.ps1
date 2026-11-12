$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"

function Wait-Live([string]$serviceName) {
    $deadline = (Get-Date).AddMinutes(3)
    do {
        try {
            $r = Invoke-RestMethod "$base/health/live" -TimeoutSec 3
            if ($r.live) { return }
        } catch {}
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)

    docker compose --profile recovery logs --tail=150 $serviceName
    throw "$serviceName did not become live on 8080"
}

Write-Host "[ROLLBACK 1/7] Prepare recovery data volume for non-root runtime"
docker compose --profile recovery run --rm --user 0 --no-deps father-chassis-recovery sh -c "mkdir -p /app/data-recovery && chown -R father:father /app/data-recovery"
if ($LASTEXITCODE -ne 0) { throw "recovery data volume ownership preparation failed" }

Write-Host "[ROLLBACK 2/7] Stop canonical modular API"
docker compose stop father-chassis
if ($LASTEXITCODE -ne 0) { throw "could not stop canonical modular service" }

Write-Host "[ROLLBACK 3/7] Start recovery runtime on canonical port 8080"
docker compose --profile recovery up -d --no-build father-chassis-recovery
if ($LASTEXITCODE -ne 0) { throw "recovery runtime start failed" }
Wait-Live "father-chassis-recovery"

Write-Host "[ROLLBACK 4/7] Prove recovery service identity and basic contracts"
$root = Invoke-RestMethod "$base/"
if ($root.service -ne "FATHER Chassis / Factory") { throw "8080 is not served by recovery runtime" }

$ready = Invoke-RestMethod "$base/health/ready"
if (-not $ready.ready) { throw "recovery readiness failed" }

$body = @{
    source = "rollback-qualification"
    text = "Recovery runtime is available as a controlled rollback target for FATHER Chassis."
} | ConvertTo-Json
Invoke-RestMethod "$base/ingest" -Method Post -ContentType "application/json" -Body $body | Out-Null

$runBody = @{ input = "What is the recovery runtime used for?" } | ConvertTo-Json
$run = Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $runBody
if ([string]::IsNullOrWhiteSpace($run.trace_id)) { throw "recovery trace missing" }

Write-Host "[ROLLBACK 5/7] Stop recovery runtime after rollback proof"
docker compose --profile recovery stop father-chassis-recovery
if ($LASTEXITCODE -ne 0) { throw "could not stop recovery runtime" }

Write-Host "[ROLLBACK 6/7] Restore canonical modular API"
docker compose up -d --no-build father-chassis
if ($LASTEXITCODE -ne 0) { throw "could not restore canonical modular service" }
Wait-Live "father-chassis"

Write-Host "[ROLLBACK 7/7] Prove canonical modular service is restored"
$restored = Invoke-RestMethod "$base/"
if ($restored.service -ne "FATHER Chassis Modular") { throw "canonical modular API was not restored after rollback test" }

Write-Host ""
Write-Host "CANONICAL ROLLBACK QUALIFICATION: PASS"
