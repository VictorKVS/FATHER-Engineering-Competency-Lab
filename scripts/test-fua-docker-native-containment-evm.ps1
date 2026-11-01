$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

Write-Host "=== FUA-001 DOCKER NATIVE CONTAINMENT EVM ==="

$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
    Write-Host "DOCKER CONTAINMENT RESULT: BLOCKED - DOCKER_NOT_FOUND"
    exit 30
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "DOCKER CONTAINMENT RESULT: BLOCKED - DOCKER_ENGINE_UNAVAILABLE"
    exit 31
}

$Image = "python:3.12-alpine"

Write-Host ""
Write-Host "00. Ensure test image"
docker pull $Image | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "failed to pull containment test image"
}

$common = @(
    "run","--rm",
    "--network","none",
    "--read-only",
    "--cap-drop","ALL",
    "--security-opt","no-new-privileges:true",
    "--user","65534:65534",
    "--memory","256m",
    "--cpus","1.0",
    "--pids-limit","32",
    "--tmpfs","/tmp:rw,noexec,nosuid,nodev,size=32m",
    $Image
)

Write-Host ""
Write-Host "01. Non-root identity"
$out = & docker @common python -c "import os; print('UID='+str(os.getuid())); print('GID='+str(os.getgid()))"
$out | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0 -or ($out -notcontains "UID=65534")) {
    throw "container did not run as non-root"
}
Write-Host "NON_ROOT        : PASS"

Write-Host ""
Write-Host "02. Read-only root filesystem"
$out = & docker @common python -c "from pathlib import Path; import sys; p=Path('/etc/fua-write-test'); 
try:
 p.write_text('x')
except OSError as e:
 print('ROOTFS_DENY=PASS'); print('ERROR_TYPE='+type(e).__name__)
else:
 print('ROOTFS_DENY=FAIL'); sys.exit(21)"
$out | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0 -or ($out -notcontains "ROOTFS_DENY=PASS")) {
    throw "read-only root filesystem was not enforced"
}

Write-Host ""
Write-Host "03. Writable bounded tmpfs"
$out = & docker @common python -c "from pathlib import Path; p=Path('/tmp/fua.txt'); p.write_text('PASS'); print('TMPFS_WRITE='+p.read_text())"
$out | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0 -or ($out -notcontains "TMPFS_WRITE=PASS")) {
    throw "bounded tmpfs was not writable"
}

Write-Host ""
Write-Host "04. Network isolation"
$out = & docker @common python -c "import socket,sys;
try:
 socket.create_connection(('1.1.1.1',443),2)
except OSError as e:
 print('NETWORK_DENY=PASS'); print('ERROR_TYPE='+type(e).__name__)
else:
 print('NETWORK_DENY=FAIL'); sys.exit(22)"
$out | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0 -or ($out -notcontains "NETWORK_DENY=PASS")) {
    throw "network isolation was not enforced"
}

Write-Host ""
Write-Host "05. No host mounts"
$out = & docker @common python -c "from pathlib import Path; 
targets=['/host','/mnt/host','/workspace','/repo'];
present=[p for p in targets if Path(p).exists()];
print('HOST_MOUNTS_PRESENT='+str(len(present)));
raise SystemExit(0 if not present else 23)"
$out | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0 -or ($out -notcontains "HOST_MOUNTS_PRESENT=0")) {
    throw "unexpected host mount detected"
}
Write-Host "NO_HOST_MOUNTS  : PASS"

Write-Host ""
Write-Host "06. Capability boundary"
$out = & docker @common sh -c "grep '^CapEff:' /proc/self/status; grep '^NoNewPrivs:' /proc/self/status"
$out | ForEach-Object { Write-Host $_ }
$cap = $out | Where-Object { $_ -like "CapEff:*" } | Select-Object -First 1
$nnp = $out | Where-Object { $_ -like "NoNewPrivs:*" } | Select-Object -First 1
if ($cap -notmatch "0000000000000000") {
    throw "effective capabilities are not empty"
}
if ($nnp -notmatch "1$") {
    throw "no-new-privileges is not active"
}
Write-Host "CAP_DROP_ALL    : PASS"
Write-Host "NO_NEW_PRIVS    : PASS"

Write-Host ""
Write-Host "07. Memory limit"
$out = & docker @common sh -c "cat /sys/fs/cgroup/memory.max 2>/dev/null || true"
$out | ForEach-Object { Write-Host ("MEMORY_MAX      : {0}" -f $_) }
$memoryLine = $out | Select-Object -First 1
if (-not $memoryLine) {
    throw "memory cgroup limit unavailable"
}
if ($memoryLine -eq "max") {
    throw "memory limit is not enforced"
}
if ([int64]$memoryLine -gt 268435456) {
    throw "memory limit exceeds 256 MiB"
}
Write-Host "MEMORY_LIMIT    : PASS"

Write-Host ""
Write-Host "DOCKER NATIVE CONTAINMENT EVM RESULT: PASS"
