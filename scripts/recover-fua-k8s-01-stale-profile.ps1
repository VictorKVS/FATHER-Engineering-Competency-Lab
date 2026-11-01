param(
    [switch]$ApproveRecreateStaleProfile
)

$ErrorActionPreference = "Stop"
$Profile = "otus-k8s"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

Write-Host "=== FUA-001 KUBERNETES 2.01 RECOVERY / STALE MINIKUBE PROFILE ==="

$Minikube = (Get-Command minikube -ErrorAction SilentlyContinue).Source
if (-not $Minikube) {
    $fallback = "C:\Program Files\Kubernetes\Minikube\minikube.exe"
    if (Test-Path $fallback) { $Minikube = $fallback }
}
if (-not $Minikube) { throw "minikube not found" }

$ProfileRoot = Join-Path $env:USERPROFILE ".minikube"
$MachineDir = Join-Path $ProfileRoot "machines\$Profile"
$ProfileDir = Join-Path $ProfileRoot "profiles\$Profile"
$Config = Join-Path $MachineDir "config.json"

Write-Host ""
Write-Host "01. Diagnose stale profile"
Write-Host ("MACHINE DIR       : {0}" -f $MachineDir)
Write-Host ("PROFILE DIR       : {0}" -f $ProfileDir)
Write-Host ("CONFIG.JSON       : {0}" -f $Config)
Write-Host ("MACHINE EXISTS    : {0}" -f (Test-Path $MachineDir))
Write-Host ("PROFILE EXISTS    : {0}" -f (Test-Path $ProfileDir))
Write-Host ("CONFIG EXISTS     : {0}" -f (Test-Path $Config))

$stale = ((Test-Path $MachineDir) -or (Test-Path $ProfileDir)) -and (-not (Test-Path $Config))
if (-not $stale) {
    Write-Host "STALE PROFILE      : NOT CONFIRMED"
    Write-Host "RECOVERY RESULT    : BLOCKED - PROFILE_STATE_NOT_STALE"
    exit 3
}
Write-Host "STALE PROFILE      : CONFIRMED"

Write-Host ""
Write-Host "02. Preserve residual state"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupRoot = Join-Path $Repo "factory\evidence\k8s-recovery\$Profile-$stamp"
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

if (Test-Path $MachineDir) {
    Copy-Item $MachineDir (Join-Path $BackupRoot "machine") -Recurse -Force
}
if (Test-Path $ProfileDir) {
    Copy-Item $ProfileDir (Join-Path $BackupRoot "profile") -Recurse -Force
}
$diag = [ordered]@{
    timestamp = (Get-Date).ToString("o")
    profile = $Profile
    machine_dir_exists = (Test-Path $MachineDir)
    profile_dir_exists = (Test-Path $ProfileDir)
    config_json_exists = (Test-Path $Config)
    decision = "STALE_PROFILE_CONFIRMED"
}
$diag | ConvertTo-Json | Set-Content (Join-Path $BackupRoot "diagnostic.json") -Encoding UTF8
Write-Host ("BACKUP             : {0}" -f $BackupRoot)
Write-Host "RESIDUAL BACKUP     : PASS"

Write-Host ""
Write-Host "03. Human destructive-operation gate"
if (-not $ApproveRecreateStaleProfile) {
    Write-Host "DELETE APPROVAL     : NOT PROVIDED"
    Write-Host "RECOVERY RESULT     : BLOCKED - HUMAN_APPROVAL_REQUIRED"
    Write-Host ""
    Write-Host "Re-run with:"
    Write-Host ".\scripts\recover-fua-k8s-01-stale-profile.ps1 -ApproveRecreateStaleProfile"
    exit 2
}
Write-Host "DELETE APPROVAL     : PROVIDED"

Write-Host ""
Write-Host "04. Delete only stale otus-k8s profile"
& $Minikube delete -p $Profile
if ($LASTEXITCODE -ne 0) { throw "minikube delete failed" }

# Remove residual profile directories only if minikube left them behind.
foreach ($p in @($MachineDir,$ProfileDir)) {
    if (Test-Path $p) {
        Remove-Item $p -Recurse -Force
    }
}
Write-Host "STALE PROFILE DELETE: PASS"

Write-Host ""
Write-Host "05. Recreate clean Docker-driver cluster"
& $Minikube start -p $Profile --driver=docker --cpus=4 --memory=6144
if ($LASTEXITCODE -ne 0) { throw "minikube recreate failed" }

Write-Host ""
Write-Host "06. Verify recreated profile"
& $Minikube status -p $Profile
if ($LASTEXITCODE -ne 0) { throw "minikube status failed after recreate" }

Write-Host ""
Write-Host "FUA-001 KUBERNETES 2.01 RECOVERY RESULT: PASS"
