$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 FINAL EVIDENCE AUDIT EVM ==="

& $Py -c @'
from pathlib import Path
from father_fua.evidence_auditor import audit_repository, repository_gate

root=Path(".")
findings=audit_repository(root)

print("FINDING COUNT   :",len(findings))
for f in findings:
    print("{}|{}|{}".format(f.severity,f.code,f.message))

gate=repository_gate(root)
print("REPOSITORY GATE :",gate)

raise SystemExit(0 if gate=="PASS" else 20)
'@

$Code=$LASTEXITCODE
if ($Code -ne 0) {
    throw "final evidence audit failed with exit code $Code"
}

Write-Host ""
Write-Host "FINAL EVIDENCE AUDIT RESULT: PASS"
