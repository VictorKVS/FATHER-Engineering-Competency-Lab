$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

& $Py -c @'
from father_fua.evidence_auditor import audit_repository, repository_gate
findings=audit_repository(".")
print(f"EVIDENCE AUDIT GATE: {repository_gate('.')}")
print(f"FINDINGS: {len(findings)}")
for f in findings:
    print(f"{f.severity} {f.code}: {f.message}")
if findings:
    raise SystemExit(30)
'@

if ($LASTEXITCODE -ne 0) { throw "evidence audit failed" }
Write-Host "EVIDENCE AUDIT RESULT: PASS"
