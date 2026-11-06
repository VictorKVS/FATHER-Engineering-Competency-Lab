$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 FAULT / RECOVERY STRESS EVM ==="

$TempPy = Join-Path $env:TEMP "fua-fault-recovery-stress-evm.py"

@'
from dataclasses import replace

from father_fua.audit import AuditLog
from father_fua.evidence import create_evidence, verify_evidence
from father_fua.recovery import retry

transient_pass=0
security_denial_pass=0
audit_pass=0
evidence_pass=0

print("01. TRANSIENT RECOVERY")
for _ in range(100):
    state={"n":0}
    def op():
        state["n"] += 1
        if state["n"] < 3:
            raise RuntimeError("transient")
        return "OK"
    if retry(op,attempts=3)=="OK" and state["n"]==3:
        transient_pass += 1
print("TRANSIENT PASS  :",transient_pass,"/100")
if transient_pass != 100:
    raise SystemExit(20)

print("")
print("02. SECURITY DENIAL MUST NOT RETRY")
for _ in range(100):
    state={"n":0}
    def denied():
        state["n"] += 1
        raise PermissionError("policy denied")
    try:
        retry(denied,attempts=5)
    except PermissionError:
        if state["n"]==1:
            security_denial_pass += 1
print("DENIAL PASS     :",security_denial_pass,"/100")
if security_denial_pass != 100:
    raise SystemExit(21)

print("")
print("03. AUDIT CHAIN TAMPER DETECTION")
for i in range(50):
    audit=AuditLog()
    for n in range(20):
        audit.append(kind="stress",actor="FUA-001",correlation_id=f"C{i}",detail={"n":n})
    if not audit.verify():
        raise SystemExit(22)
    audit.events[10]=replace(audit.events[10],detail={"n":"tampered"})
    if audit.verify():
        raise SystemExit(23)
    audit_pass += 1
print("AUDIT PASS      :",audit_pass,"/50")

print("")
print("04. EVIDENCE TAMPER DETECTION")
for i in range(100):
    ev=create_evidence(
        f"E-FRS-{i}",
        "FAULT_RECOVERY_STRESS",
        {"i":i,"status":"PASS"},
        provenance="evm",
        correlation_id=f"C-{i}",
        created_at=float(i+1),
    )
    if not verify_evidence(ev):
        raise SystemExit(24)
    tampered=replace(ev,payload={"i":i,"status":"FAIL"})
    if verify_evidence(tampered):
        raise SystemExit(25)
    evidence_pass += 1
print("EVIDENCE PASS   :",evidence_pass,"/100")

print("")
print("FUA-001 FAULT / RECOVERY STRESS EVM RESULT: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) {
    throw "fault/recovery stress EVM failed with exit code $Code"
}
