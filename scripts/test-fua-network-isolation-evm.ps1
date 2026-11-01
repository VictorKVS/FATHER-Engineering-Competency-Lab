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
    Write-Host "01. Baseline connectivity"
    $baseline = & $Py -c "import socket; s=socket.create_connection(('127.0.0.1',11434),3); s.close(); print('CONNECT=PASS')"
    if ($LASTEXITCODE -ne 0 -or $baseline -notmatch "CONNECT=PASS") {
        throw "baseline loopback connectivity to Ollama is not available"
    }
    Write-Host $baseline

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
try:
    s=socket.create_connection(("127.0.0.1",11434),2)
except OSError as e:
    print("NETWORK_DENY=PASS")
    print("ERROR_TYPE={}".format(type(e).__name__))
else:
    s.close()
    print("NETWORK_DENY=FAIL")
    raise SystemExit(21)
'@ | Set-Content -Path $TempPy -Encoding UTF8

    try {
        & $Py $TempPy
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