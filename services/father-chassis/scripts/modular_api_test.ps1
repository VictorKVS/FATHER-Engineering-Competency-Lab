$ErrorActionPreference = "Stop"
$base = "http://localhost:8081"

Write-Host "[1/8] Start modular API"
docker compose up -d --build father-chassis-modular
if ($LASTEXITCODE -ne 0) { throw "modular container start failed" }

Write-Host "[2/8] Wait for readiness"
$deadline = (Get-Date).AddMinutes(3)
$ready = $false
do {
    try {
        $r = Invoke-RestMethod "$base/health/ready" -TimeoutSec 3
        if ($r.ready) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
} while ((Get-Date) -lt $deadline)
if (-not $ready) {
    docker compose logs --tail=150 father-chassis-modular
    throw "modular API did not become ready"
}

Write-Host "[3/8] Probe real local model"
$probe = Invoke-RestMethod "$base/models/local/probe"
if (-not $probe.reachable -or -not $probe.selected_present) {
    throw "modular API cannot reach selected local model"
}

Write-Host "[4/8] Ingest modular evidence"
$ingest = @{
    source = "qualification://modular-api"
    text = "FATHER modular API uses ChassisRuntime with workflow, RAG, model routing, evidence, audit, policy and tool registry."
} | ConvertTo-Json
Invoke-RestMethod "$base/ingest" -Method Post -ContentType "application/json" -Body $ingest | Out-Null

Write-Host "[5/8] Run real modular inference"
$body = @{ input = "Which capabilities are provided by the FATHER modular API?" } | ConvertTo-Json
$result = Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 120
if ([string]::IsNullOrWhiteSpace($result.trace_id)) { throw "trace_id missing" }
if ([string]::IsNullOrWhiteSpace($result.output)) { throw "output missing" }
if ($result.evidence.Count -lt 1) { throw "evidence missing" }

Write-Host "[6/8] Validate audit"
$audit = Invoke-RestMethod "$base/audit/$($result.trace_id)"
if ($audit.events.Count -lt 6) { throw "modular audit chain too short" }

Write-Host "[7/8] Emergency stop / resume"
Invoke-RestMethod "$base/control/stop" -Method Post | Out-Null
$blocked = $false
try {
    Invoke-RestMethod "$base/health/ready" -TimeoutSec 3 | Out-Null
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 503) { $blocked = $true }
}
if (-not $blocked) { throw "emergency stop did not block readiness" }
Invoke-RestMethod "$base/control/resume" -Method Post | Out-Null

Write-Host "[8/8] OSINT product through modular runtime"
$osint = @{
    query = "What is FATHER modular architecture?"
    sources = @(
        @{
            source_id = "mod-src-001"
            source_type = "document"
            title = "Modular Core"
            content = "FATHER modular architecture separates runtime, state, workflow, model routing, RAG, tools, evidence and audit."
            uri = "local://modular-core"
        }
    )
} | ConvertTo-Json -Depth 10
$prod = Invoke-RestMethod "$base/products/osint/workflow" -Method Post -ContentType "application/json" -Body $osint -TimeoutSec 120
if (-not $prod.passed) { throw "modular OSINT product qualification failed" }

Write-Host ""
Write-Host "MODULAR API QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 10
