$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"

function Wait-Ready([string]$serviceName) {
    $deadline = (Get-Date).AddMinutes(3)
    do {
        try {
            $r = Invoke-RestMethod "$base/health/ready" -TimeoutSec 3
            if ($r.ready) { return }
        } catch {}
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)

    docker compose logs --tail=150 $serviceName
    throw "$serviceName did not become ready on 8080"
}

Write-Host "[CUTOVER 1/8] Build canonical modular image"
docker compose build father-chassis
if ($LASTEXITCODE -ne 0) { throw "canonical image build failed" }

Write-Host "[CUTOVER 2/8] Prepare canonical data volume for non-root runtime"
docker compose run --rm --user 0 --no-deps father-chassis sh -c "mkdir -p /app/data && chown -R father:father /app/data"
if ($LASTEXITCODE -ne 0) { throw "canonical data volume ownership preparation failed" }

Write-Host "[CUTOVER 3/8] Stop recovery service if present and start canonical modular API"
docker compose --profile recovery stop father-chassis-recovery 2>$null | Out-Null
docker compose up -d --no-build father-chassis
if ($LASTEXITCODE -ne 0) { throw "canonical modular service start failed" }
Wait-Ready "father-chassis"

Write-Host "[CUTOVER 4/8] Canonical smoke qualification"
& .scriptssmoke_test.ps1

Write-Host "[CUTOVER 5/8] Canonical local LLM qualification"
& .scriptsllm_test.ps1

Write-Host "[CUTOVER 6/8] Canonical OSINT qualification"
& .scriptsosint_product_test.ps1

Write-Host "[CUTOVER 7/8] Canonical Factory Execution qualification"
$factoryBody = @{
    requirement = @{
        requirement_id = "REQ-CANONICAL-CUTOVER-001"
        title = "Canonical cutover knowledge analyst"
        needs = @("analyze_documents", "create_report", "enforce_policy", "run_workflow")
        required_permissions = @("execute:analysis")
        metadata = @{ agent_id = "canonical-factory-agent" }
    }
    input = "What is FATHER Chassis and which shared capabilities does it provide?"
} | ConvertTo-Json -Depth 10

$factory = Invoke-RestMethod "$base/factory/solutions/execute" -Method Post -ContentType "application/json" -Body $factoryBody -TimeoutSec 120
if ($factory.status -ne "EXECUTED") { throw "canonical factory execution failed" }
if ($factory.agent_id -ne "canonical-factory-agent") { throw "canonical factory agent identity mismatch" }
if (-not $factory.qualification.qualified) { throw "canonical factory qualification did not pass" }
if ([string]::IsNullOrWhiteSpace($factory.qualification.record_hash)) { throw "canonical qualification hash missing" }

Write-Host "[CUTOVER 8/8] Validate canonical service identity"
$root = Invoke-RestMethod "$base/"
if ($root.service -ne "FATHER Chassis Modular") { throw "8080 is not served by modular API" }

Write-Host ""
Write-Host "CANONICAL MODULAR CUTOVER QUALIFICATION: PASS"
$factory | ConvertTo-Json -Depth 12
