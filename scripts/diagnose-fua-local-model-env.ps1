$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 LOCAL MODEL ENVIRONMENT DIAGNOSTIC ==="

Write-Host ""
Write-Host "01. Running services/processes"
$procs = Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -match 'ollama|lmstudio|llama|kobold|vllm'
}
if ($procs) {
    $procs | Select-Object ProcessName, Id, Path | Format-Table -AutoSize
} else {
    Write-Host "No known local-model process detected"
}

Write-Host ""
Write-Host "02. Known executables"
$commands = @('ollama','lmstudio')
foreach ($cmd in $commands) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($c) {
        Write-Host "$cmd => $($c.Source)"
    }
}

Write-Host ""
Write-Host "03. Local listening ports"
$ports = 11434,8000,1234,8080
foreach ($port in $ports) {
    $listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
    if ($listener) {
        Write-Host "LISTEN $port => PID $($listener.OwningProcess -join ',')"
    } else {
        Write-Host "CLOSED $port"
    }
}

Write-Host ""
Write-Host "04. FUA API discovery"
& $Py -c @'
from father_fua.local_models import discover_local_models
models=discover_local_models()
print(f"DISCOVERED_MODELS={len(models)}")
for m in models:
    print(f"{m.transport}|{m.model_id}|{m.base_url}")
'@

Write-Host ""
Write-Host "05. Candidate model roots"
$roots = @(
    'F:\FATHER_MODELS',
    'G:\1',
    "$env:USERPROFILE\.ollama\models",
    "$env:LOCALAPPDATA\LM Studio\models"
)
foreach ($root in $roots) {
    if (Test-Path $root) {
        $files = Get-ChildItem $root -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in '.gguf','.bin','.safetensors' } |
            Select-Object -First 25 FullName, Length
        Write-Host "ROOT: $root"
        if ($files) {
            $files | Format-Table -AutoSize
        } else {
            Write-Host "  no candidate model files in first scan"
        }
    }
}

Write-Host ""
Write-Host "LOCAL MODEL ENVIRONMENT DIAGNOSTIC: COMPLETE"
