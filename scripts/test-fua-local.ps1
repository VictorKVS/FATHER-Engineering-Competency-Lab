$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

Write-Host "=== FUA-001 LOCAL EVM TEST ==="
Write-Host "Repo: $Repo"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python not found"
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$Py = Join-Path $Repo ".venv\Scripts\python.exe"
$Pip = Join-Path $Repo ".venv\Scripts\pip.exe"

& $Py -m pip install --upgrade pip
& $Pip install -e ".[test]"

Write-Host "
=== 01. PYTEST ==="
& $Py -m pytest
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }

Write-Host "
=== 02. START API ==="
$env:FUA_DEV_TOKEN = "dev-token"
$Proc = Start-Process -FilePath $Py -ArgumentList "-m","uvicorn","father_fua.api:app","--host","127.0.0.1","--port","8091" -PassThru -WindowStyle Hidden

try {
    $ok = $false
    1..30 | ForEach-Object {
        Start-Sleep -Milliseconds 300
        try {
            $h = Invoke-RestMethod "http://127.0.0.1:8091/health"
            if ($h.status -eq "ok") { $ok = $true; break }
        } catch {}
    }
    if (-not $ok) { throw "API did not become healthy" }

    Write-Host "
=== 03. API SMOKE ==="
    $Headers = @{ Authorization = "Bearer dev-token" }

    $Agent = @{
        agent_id = "FUA-EVM-001"
        name = "FUA EVM Test Agent"
        version = "0.1"
        owner = "FATHER"
        mission_profile = "LOCAL-EVM-TEST"
        environment = "WORKSTATION"
        trust_level = "STANDARD"
    } | ConvertTo-Json

    $created = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8091/v1/agents" -Headers $Headers -ContentType "application/json" -Body $Agent
    Write-Host "AGENT: $($created.agent_id)"
    Write-Host "HASH : $($created.manifest_sha256)"

    $ready = Invoke-RestMethod -Uri "http://127.0.0.1:8091/v1/agents/FUA-EVM-001/readiness" -Headers $Headers
    Write-Host "INSTALLATION PERMIT: $($ready.installation_permit)"
    Write-Host "BLOCKING GATES: $($ready.blocking_gates -join ', ')"

    if ($ready.installation_permit -ne "DENIED") {
        throw "Prototype must not claim installation approval"
    }

    Write-Host "
LOCAL EVM RESULT: PASS"
}
finally {
    if ($Proc -and -not $Proc.HasExited) {
        Stop-Process -Id $Proc.Id -Force
    }
}
