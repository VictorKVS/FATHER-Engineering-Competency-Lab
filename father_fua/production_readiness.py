from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProductionReadinessFinding:
    code: str
    severity: str
    status: str
    message: str


def review_production_readiness(root: str | Path) -> list[ProductionReadinessFinding]:
    root=Path(root)
    manifest=json.loads(
        (root/"factory/chassis/FUA-001/manifest.json").read_text(encoding="utf-8")
    )
    findings=[]

    required_pass={
        "product_test_evm":"PASS",
        "pilot_test_evm":"PASS",
        "reliability_gate_evm":"PASS",
        "sandbox_stress_evm":"PASS",
        "fault_recovery_stress_evm":"PASS",
        "full_polygon_real_runtime":"PASS",
        "network_isolation_evm":"PASS",
        "filesystem_acl_evm":"PASS",
    }
    for key,expected in required_pass.items():
        actual=(manifest.get(key) or {}).get("status")
        if actual!=expected:
            findings.append(ProductionReadinessFinding(
                code="MANDATORY_GATE_NOT_PASS",
                severity="HIGH",
                status="BLOCK",
                message=f"{key}: expected {expected}, got {actual}",
            ))

    restricted=manifest.get("restricted_trustlevel_evm") or {}
    if restricted.get("status")=="BLOCKED_BY_OS_CAPABILITY":
        findings.append(ProductionReadinessFinding(
            code="OS_TRUST_BOUNDARY_NOT_PROVEN",
            severity="HIGH",
            status="BLOCK",
            message="Restricted token / AppContainer / Low Integrity boundary not proven on target OS.",
        ))

    process_sb=manifest.get("process_sandbox_evm") or {}
    if process_sb.get("final_sandbox_certified") is not True:
        findings.append(ProductionReadinessFinding(
            code="FINAL_NATIVE_CONTAINMENT_NOT_CERTIFIED",
            severity="HIGH",
            status="BLOCK",
            message="Hostile native-code containment is not certified.",
        ))

    if manifest.get("production_ready") is not False:
        findings.append(ProductionReadinessFinding(
            code="PREMATURE_PRODUCTION_READY",
            severity="CRITICAL",
            status="BLOCK",
            message="production_ready must remain false during review.",
        ))

    return findings


def production_readiness_decision(root: str | Path) -> str:
    return "PASS" if not review_production_readiness(root) else "BLOCKED"
