param(
    [switch]$ApproveRecreateCertBrokenProfile
)

$ErrorActionPreference = "Stop"
$Profile = "otus-k8s"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

Write-Host "=== FUA-001 KUBERNETES 2.01 RECOVERY / INVALID APISERVER CERT SAN ==="

$Minikube = (Get-Command minikube -ErrorAction SilentlyContinue).Source
if (-not $Minikube) {
    $fallback = "C:\\Program Files\\Kubernetes\\Minikube\\minikube.exe"
    if (Test-Path $fallback) { $Minikube = $fallback }
}
if (-not $Minikube) { throw "minikube not found" }

Write-Host ""
Write-Host "01. Preserve current diagnostic state"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupRoot = Join-Path $Repo "factory\\evidence\\k8s-recovery\\$Profile-certsan-$stamp"
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

$MachineDir = Join-Path $env:USERPROFILE ".minikube\\machines\\$Profile"
$ProfileDir = Join-Path $env:USERPROFILE ".minikube\\profiles\\$Profile"
if (Test-Path $MachineDir) { Copy-Item $MachineDir (Join-Path $BackupRoot "machine") -Recurse -Force }
if (Test-Path $ProfileDir) { Copy-Item $ProfileDir (Join-Path $BackupRoot "profile") -Recurse -Force }

try {
    & $Minikube logs -p $Profile --file=(Join-Path $BackupRoot "minikube.log") 2>$null
} catch {}

[ordered]@{
    timestamp=(Get-Date).ToString("o")
    profile=$Profile
    failure_class="K8S_INVALID_CERT_HOSTNAME"
    recovery="explicit_apiserver_sans"
    apiserver_name="control-plane.minikube.internal"
    apiserver_names=@("localhost","control-plane.minikube.internal")
} | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $BackupRoot "diagnostic.json") -Encoding UTF8

Write-Host ("BACKUP             : {0}" -f $BackupRoot)
Write-Host "DIAGNOSTIC BACKUP   : PASS"

Write-Host ""
Write-Host "02. Human destructive-operation gate"
if (-not $ApproveRecreateCertBrokenProfile) {
    Write-Host "DELETE APPROVAL     : NOT PROVIDED"
    Write-Host "RECOVERY RESULT     : BLOCKED - HUMAN_APPROVAL_REQUIRED"
    exit 2
}
Write-Host "DELETE APPROVAL     : PROVIDED"

Write-Host ""
Write-Host "03. Delete only failed otus-k8s profile"
& $Minikube delete -p $Profile
if ($LASTEXITCODE -ne 0) { throw "minikube delete failed" }
Write-Host "PROFILE DELETE      : PASS"

Write-Host ""
Write-Host "04. Recreate with explicit API-server SANs"
& $Minikube start -p $Profile --driver=docker --cpus=4 --memory=6144 --apiserver-name=control-plane.minikube.internal --apiserver-names=localhost,control-plane.minikube.internal
if ($LASTEXITCODE -ne 0) { throw "minikube recreate with explicit SANs failed" }

Write-Host ""
Write-Host "05. Verify cluster"
& $Minikube status -p $Profile
if ($LASTEXITCODE -ne 0) { throw "minikube status failed" }

Write-Host ""
Write-Host "FUA-001 KUBERNETES 2.01 CERTSAN RECOVERY RESULT: PASS"
