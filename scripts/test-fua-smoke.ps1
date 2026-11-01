$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

Write-Host "=== FUA-001 LOCAL HTTP / FULL ASSEMBLY SMOKE ==="

$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    throw ".venv Python not found. Run test-fua-local.ps1 first."
}

$env:FUA_DEV_TOKEN = "dev-token"
$Proc = Start-Process -FilePath $Py -ArgumentList "-m","uvicorn","father_fua.api:app","--host","127.0.0.1","--port","8091" -PassThru -WindowStyle Hidden

try {
    $ok = $false
    for ($i = 1; $i -le 30; $i++) {
        Start-Sleep -Milliseconds 300
        try {
            $h = Invoke-RestMethod "http://127.0.0.1:8091/health"
            if ($h.status -eq "ok") {
                $ok = $true
                break
            }
        } catch {}
    }

    if (-not $ok) { throw "API did not become healthy" }

    Write-Host "HEALTH          : PASS"

    $Headers = @{ Authorization = "Bearer dev-token" }

    $AssemblyBody = @{ mission = "FATHER universal agent architecture" } | ConvertTo-Json
    $assembly = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8091/v1/assembly/run" -Headers $Headers -ContentType "application/json" -Body $AssemblyBody

    Write-Host "ASSEMBLY STATUS : $($assembly.status)"
    Write-Host "AUDIT OK        : $($assembly.audit_ok)"
    Write-Host "READINESS       : $($assembly.readiness)"
    Write-Host "EVIDENCE SHA256 : $($assembly.evidence_sha256)"

    if ($assembly.status -ne "PASS") { throw "Full assembly mission failed" }
    if (-not $assembly.audit_ok) { throw "Audit chain verification failed" }
    if ($assembly.readiness -ne "DENIED") { throw "Readiness must remain DENIED before final gates" }
    if ($assembly.evidence_sha256.Length -ne 64) { throw "Evidence hash invalid" }

    Write-Host ""
    Write-Host "LOCAL HTTP / FULL ASSEMBLY RESULT: PASS"
}
finally {
    if ($Proc -and -not $Proc.HasExited) {
        Stop-Process -Id $Proc.Id -Force
    }
}
