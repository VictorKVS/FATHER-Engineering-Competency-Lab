$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 WINDOWS NETWORK ISOLATION EVM ==="

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "ADMIN           : $isAdmin"
if (-not $isAdmin) {
    Write-Host ""
    Write-Host "NETWORK ISOLATION RESULT: BLOCKED - ADMIN_REQUIRED"
    exit 30
}

$RuleName = "FUA-001-SANDBOX-NETWORK-DENY-EVM"

function Remove-FuaRule {
    Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
}

try {
    Remove-FuaRule

    Write-Host ""
    Write-Host "01. Baseline external connectivity"
    $ProbePy = Join-Path $env:TEMP "fua-network-baseline.py"
@'
import socket

targets=[
    ("api.github.com",443),
    ("www.microsoft.com",443),
    ("1.1.1.1",443),
]
for host,port in targets:
    try:
        s=socket.create_connection((host,port),3)
    except OSError:
        continue
    else:
        s.close()
        print("CONNECT=PASS")
        print("TARGET_HOST={}".format(host))
        print("TARGET_PORT={}".format(port))
        raise SystemExit(0)
print("CONNECT=FAIL")
raise SystemExit(20)
'@ | Set-Content -Path $ProbePy -Encoding UTF8

    try {
        $baseline = & $Py $ProbePy
        $baselineCode = $LASTEXITCODE
    }
    finally {
        Remove-Item $ProbePy -Force -ErrorAction SilentlyContinue
    }

    $baseline | ForEach-Object { Write-Host $_ }

    $connectLine = $baseline | Where-Object { $_ -eq "CONNECT=PASS" } | Select-Object -First 1
    $hostLine = $baseline | Where-Object { $_ -like "TARGET_HOST=*" } | Select-Object -First 1
    $portLine = $baseline | Where-Object { $_ -like "TARGET_PORT=*" } | Select-Object -First 1

    if ($baselineCode -ne 0 -or -not $connectLine -or -not $hostLine -or -not $portLine) {
        throw "no external baseline endpoint was reachable"
    }

    $TargetHost = $hostLine -replace "^TARGET_HOST=",""
    $TargetPort = [int]($portLine -replace "^TARGET_PORT=","")
    Write-Host ("BASELINE TARGET : {0}:{1}" -f $TargetHost, $TargetPort)

    Write-Host ""
    Write-Host "02. Install temporary outbound deny rule"
    $params = @{
        DisplayName = $RuleName
        Direction = "Outbound"
        Action = "Block"
        Program = $Py
        Profile = "Any"
        Enabled = "True"
    }
    New-NetFirewallRule @params | Out-Null

    $rule = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction Stop
    Write-Host "RULE ENABLED    : $($rule.Enabled)"
    Write-Host "RULE ACTION     : $($rule.Action)"

    Write-Host ""
    Write-Host "03. Verify network denial"
    $TempPy = Join-Path $env:TEMP "fua-network-deny-check.py"
    @'
import socket
import sys

host=sys.argv[1]
port=int(sys.argv[2])

try:
    s=socket.create_connection((host,port),3)
except OSError as e:
    print("NETWORK_DENY=PASS")
    print("ERROR_TYPE={}".format(type(e).__name__))
else:
    s.close()
    print("NETWORK_DENY=FAIL")
    raise SystemExit(21)
'@ | Set-Content -Path $TempPy -Encoding UTF8

    try {
        & $Py $TempPy $TargetHost $TargetPort
        $Code = $LASTEXITCODE
    }
    finally {
        Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
    }

    if ($Code -ne 0) {
        throw "temporary firewall rule did not block sandbox Python"
    }

    Write-Host ""
    Write-Host "WINDOWS NETWORK ISOLATION EVM RESULT: PASS"
}
finally {
    Write-Host ""
    Write-Host "04. Cleanup temporary firewall rule"
    Remove-FuaRule
    $left = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue
    if ($left) {
        Write-Host "RULE CLEANUP    : FAIL"
    } else {
        Write-Host "RULE CLEANUP    : PASS"
    }
}