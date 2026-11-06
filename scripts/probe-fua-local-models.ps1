$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 LOCAL MODEL DISCOVERY ==="

& $Py -c @'
from father_fua.local_models import discover_local_models
models=discover_local_models()
print(f"FOUND: {len(models)}")
for i,m in enumerate(models,1):
    print(f"{i}. transport={m.transport} model={m.model_id} url={m.base_url} local={m.local} healthy={m.healthy}")
if not models:
    raise SystemExit(20)
'@

if ($LASTEXITCODE -eq 20) {
    Write-Host ""
    Write-Host "LOCAL MODEL DISCOVERY: NONE"
    exit 20
}
if ($LASTEXITCODE -ne 0) { throw "model discovery failed" }

Write-Host ""
Write-Host "LOCAL MODEL DISCOVERY: PASS"
