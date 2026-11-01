$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 WINDOWS FILESYSTEM ACL EVM ==="

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Host "ADMIN           : $isAdmin"

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "FILESYSTEM ACL RESULT: BLOCKED - ADMIN_REQUIRED"
    exit 30
}

$Sid = $identity.User.Value
$Root = Join-Path $env:ProgramData ("FUA-001-ACL-EVM-" + [guid]::NewGuid().ToString("N"))
$WorkDir = Join-Path $Root "work"
$ProtectedDir = Join-Path $Root "protected"
$ProtectedFile = Join-Path $ProtectedDir "sentinel.txt"

try {
    New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
    New-Item -ItemType Directory -Force -Path $ProtectedDir | Out-Null
    Set-Content -Path $ProtectedFile -Value "ORIGINAL" -Encoding ASCII

    Write-Host "SID             : $Sid"
    Write-Host "WORKDIR         : $WorkDir"
    Write-Host "PROTECTED       : $ProtectedDir"

    Write-Host ""
    Write-Host "01. Baseline workdir write"
    $workProbe = Join-Path $WorkDir "inside.txt"
    & $Py -c "from pathlib import Path; Path(r'$workProbe').write_text('PASS', encoding='utf-8'); print('WORKDIR_WRITE=PASS')"
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $workProbe)) {
        throw "sandbox workdir baseline write failed"
    }

    Write-Host ""
    Write-Host "02. Apply NTFS deny outside sandbox workdir"
    $IcaclsSid = "*" + $Sid
    & icacls.exe $ProtectedDir /deny ($IcaclsSid + ":(OI)(CI)(M)") | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "icacls deny failed"
    }

    Write-Host ""
    Write-Host "02A. Verify deny ACE"
    $aclLines = & icacls.exe $ProtectedDir
    $aclLines | ForEach-Object { Write-Host $_ }
    $aclText = $aclLines -join [Environment]::NewLine
    $AccountName = $identity.Name
    $hasDenyModify = $aclLines | Where-Object {
        $_ -match [regex]::Escape($AccountName) -and $_ -match "\(DENY\)\(M\)"
    } | Select-Object -First 1
    if (-not $hasDenyModify) {
        throw "deny ACE was not materialized for current account"
    }
    Write-Host ("DENY ACE        : PASS ({0})" -f $AccountName)

    Write-Host ""
    Write-Host "03. Verify outside write denial"
    $TempPy = Join-Path $env:TEMP "fua-acl-deny-check.py"
@'
from pathlib import Path
import sys

target=Path(sys.argv[1])

try:
    target.write_text("MUTATED", encoding="utf-8")
except (PermissionError, OSError) as e:
    print("ACL_DENY=PASS")
    print("ERROR_TYPE={}".format(type(e).__name__))
else:
    print("ACL_DENY=FAIL")
    raise SystemExit(21)
'@ | Set-Content -Path $TempPy -Encoding UTF8

    try {
        & $Py $TempPy $ProtectedFile
        $Code = $LASTEXITCODE
    }
    finally {
        Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
    }

    if ($Code -ne 0) {
        throw "protected directory write was not denied"
    }

    $sentinel = Get-Content $ProtectedFile -Raw -ErrorAction Stop
    if ($sentinel.Trim() -ne "ORIGINAL") {
        throw "protected sentinel was modified"
    }

    Write-Host "SENTINEL        : UNCHANGED"
    Write-Host ""
    Write-Host "WINDOWS FILESYSTEM ACL EVM RESULT: PASS"
}
finally {
    Write-Host ""
    Write-Host "04. Cleanup ACL and temporary directories"

    if (Test-Path $ProtectedDir) {
        & icacls.exe $ProtectedDir /remove:d ("*" + $Sid) /T /C | Out-Null
        & icacls.exe $ProtectedDir /reset /T /C | Out-Null
    }

    Remove-Item $Root -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path $Root) {
        Write-Host "ACL CLEANUP     : FAIL"
    } else {
        Write-Host "ACL CLEANUP     : PASS"
    }
}