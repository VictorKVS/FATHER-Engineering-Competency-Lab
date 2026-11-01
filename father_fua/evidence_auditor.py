from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuditFinding:
    severity: str
    code: str
    message: str


REQUIRED_EVIDENCE = (
    "factory/evidence/EVID-FUA-CI-0002.md",
    "factory/evidence/EVID-FUA-EVM-0003.md",
)

REQUIRED_RUNTIME_FILES = (
    "father_fua/full_assembly.py",
    "father_fua/real_model_runtime.py",
    "father_fua/security_layer.py",
    "father_fua/evidence.py",
    "father_fua/sandbox.py",
)

REQUIRED_TEST_FILES = (
    "tests/test_full_assembly.py",
    "tests/test_polygon_lite.py",
    "tests/test_redteam_lite.py",
    "tests/test_api_negative.py",
)


def audit_repository(root: str | Path) -> list[AuditFinding]:
    root=Path(root)
    findings:list[AuditFinding]=[]

    manifest_path=root/"factory/chassis/FUA-001/manifest.json"
    if not manifest_path.exists():
        return [AuditFinding("CRITICAL","MANIFEST_MISSING","FUA manifest missing")]

    try:
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [AuditFinding("CRITICAL","MANIFEST_INVALID",str(exc))]

    for rel in REQUIRED_EVIDENCE:
        if not (root/rel).exists():
            findings.append(AuditFinding("HIGH","EVIDENCE_MISSING",rel))

    for rel in REQUIRED_RUNTIME_FILES:
        if not (root/rel).exists():
            findings.append(AuditFinding("HIGH","RUNTIME_MISSING",rel))

    for rel in REQUIRED_TEST_FILES:
        if not (root/rel).exists():
            findings.append(AuditFinding("HIGH","TEST_MISSING",rel))

    if manifest.get("production_ready") is not False:
        findings.append(AuditFinding("CRITICAL","PREMATURE_PRODUCTION_READY","production_ready must remain false"))

    if manifest.get("installation_permit") != "DENIED":
        findings.append(AuditFinding("CRITICAL","PREMATURE_INSTALLATION_PERMIT","installation permit must remain DENIED"))

    local=manifest.get("local_evm_evidence") or {}
    if local.get("full_01_26_assembly") != "PASS":
        findings.append(AuditFinding("HIGH","LOCAL_ASSEMBLY_NOT_PROVEN","local full assembly not proven"))

    ci=manifest.get("ci_evidence") or {}
    for key in (
        "component_and_assembly_tests",
        "full_01_26_assembly",
        "live_http_full_assembly_endpoint",
        "sast_bandit",
        "sca_pip_audit",
        "secret_scan",
        "cyclonedx_sbom",
    ):
        if ci.get(key) != "PASS":
            findings.append(AuditFinding("HIGH","CI_GATE_NOT_PASS",key))

    return findings


def repository_gate(root: str | Path) -> str:
    findings=audit_repository(root)
    return "PASS" if not findings else "DENY"
