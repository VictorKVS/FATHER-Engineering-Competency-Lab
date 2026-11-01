param(
    [switch]$ApproveRecreateCertBrokenProfile
)

$ErrorActionPreference = "Stop"
$Profile = "otus-k8s"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

Write-Host "=== FUA-001 KUBERNETES 2.01 RECOVERY / WINDOWS ACL + APISERVER SAN ==="

$Minikube = (Get-Command minikube -ErrorAction SilentlyContinue).Source
if (-not $Minikube) {
    $fallback = "C:\\Program Files\\Kubernetes\\Minikube\\minikube.exe"
    if (Test-Path $fallback) { $Minikube = $fallback }
}
if (-not $Minikube) { throw "minikube not found" }

$MachineDir = Join-Path $env:USERPROFILE ".minikube\\machines\\$Profile"
$ProfileDir = Join-Path $env:USERPROFILE ".minikube\\profiles\\$Profile"
$KeyPath = Join-Path $MachineDir "id_rsa"
$Sid = ([System.Security.Principal.WindowsIdentity]::GetCurrent()).User.Value
$Grant = "*$($Sid):F"

Write-Host ""
Write-Host "01. Preserve safe diagnostic metadata only"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupRoot = Join-Path $Repo "factory\\evidence\\k8s-recovery\\$Profile-acl-certsan-$stamp"
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

[ordered]@{
    timestamp=(Get-Date).ToString("o")
    profile=$Profile
    failure_classes=@("WINDOWS_ID_RSA_ACCESS_DENIED","K8S_INVALID_CERT_HOSTNAME")
    machine_dir_exists=(Test-Path $MachineDir)
    profile_dir_exists=(Test-Path $ProfileDir)
    key_exists=(Test-Path $KeyPath)
    current_user_sid=$Sid
    sensitive_key_copied=$false
    recovery="repair_profile_acl_then_recreate_with_explicit_apiserver_sans"
} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $BackupRoot "diagnostic.json") -Encoding UTF8

if (Test-Path $ProfileDir) {
    Get-ChildItem $ProfileDir -Force -ErrorAction SilentlyContinue |
        Select-Object Name,Length,LastWriteTime |
        ConvertTo-Json -Depth 3 |
        Set-Content (Join-Path $BackupRoot "profile-directory-metadata.json") -Encoding UTF8
}
if (Test-Path $MachineDir) {
    Get-ChildItem $MachineDir -Force -ErrorAction SilentlyContinue |
        Select-Object Name,Length,LastWriteTime |
        ConvertTo-Json -Depth 3 |
        Set-Content (Join-Path $BackupRoot "machine-directory-metadata.json") -Encoding UTF8
}
Write-Host ("BACKUP             : {0}" -f $BackupRoot)
Write-Host "PRIVATE KEY COPIED  : False"
Write-Host "DIAGNOSTIC METADATA : PASS"

Write-Host ""
Write-Host "02. Human destructive-operation gate"
if (-not $ApproveRecreateCertBrokenProfile) {
    Write-Host "DELETE APPROVAL     : NOT PROVIDED"
    Write-Host "RECOVERY RESULT     : BLOCKED - HUMAN_APPROVAL_REQUIRED"
    exit 2
}
Write-Host "DELETE APPROVAL     : PROVIDED"

Write-Host ""
Write-Host "03. Repair ACL only on failed otus-k8s machine directory"
if (Test-Path $MachineDir) {
    & takeown.exe /F $MachineDir /R /D Y | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "takeown failed for otus-k8s machine directory" }

    & icacls.exe $MachineDir /grant:r $Grant /T /C /Q | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "icacls grant failed for otus-k8s machine directory" }

    if (Test-Path $KeyPath) {
        Get-Content $KeyPath -TotalCount 0 -ErrorAction Stop | Out-Null
        Write-Host "ID_RSA READ         : PASS"
    }
}
Write-Host "PROFILE ACL REPAIR  : PASS"

Write-Host ""
Write-Host "04. Delete only failed otus-k8s profile"
& $Minikube delete -p $Profile
if ($LASTEXITCODE -ne 0) {
    Write-Host "MINIKUBE DELETE     : FAILED; cleaning only otus-k8s residual directories"
}

foreach ($p in @($MachineDir,$ProfileDir)) {
    if (Test-Path $p) {
        & takeown.exe /F $p /R /D Y | Out-Null
        & icacls.exe $p /grant:r $Grant /T /C /Q | Out-Null
        Remove-Item $p -Recurse -Force -ErrorAction Stop
    }
}
Write-Host "PROFILE DELETE      : PASS"

Write-Host ""
Write-Host "05. Recreate with explicit API-server SANs"
& $Minikube start -p $Profile --driver=docker --cpus=4 --memory=6144 --apiserver-name=control-plane.minikube.internal --apiserver-names=localhost,control-plane.minikube.internal
if ($LASTEXITCODE -ne 0) { throw "minikube recreate with explicit SANs failed" }

Write-Host ""
Write-Host "06. Verify cluster"
& $Minikube status -p $Profile
if ($LASTEXITCODE -ne 0) { throw "minikube status failed" }

Write-Host ""
Write-Host "FUA-001 KUBERNETES 2.01 ACL/CERTSAN RECOVERY RESULT: PASS"
