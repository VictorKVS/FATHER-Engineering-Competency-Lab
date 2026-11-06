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

    docker_containment=manifest.get("docker_native_containment_evm") or {}
    docker_profile_pass=(
        docker_containment.get("status")=="PASS"
        and docker_containment.get("network_none") is True
        and docker_containment.get("read_only_rootfs") is True
        and docker_containment.get("non_root") is True
        and docker_containment.get("cap_drop_all") is True
        and docker_containment.get("no_new_privileges") is True
        and docker_containment.get("no_host_mounts") is True
        and docker_containment.get("memory_limit") is True
    )

    restricted=manifest.get("restricted_trustlevel_evm") or {}
    if restricted.get("status")=="BLOCKED_BY_OS_CAPABILITY" and not docker_profile_pass:
        findings.append(ProductionReadinessFinding(
            code="OS_TRUST_BOUNDARY_NOT_PROVEN",
            severity="HIGH",
            status="BLOCK",
            message="Windows restricted-token boundary is unavailable and equivalent Docker containment is not proven.",
        ))

    process_sb=manifest.get("process_sandbox_evm") or {}
    if process_sb.get("final_sandbox_certified") is not True and not docker_profile_pass:
        findings.append(ProductionReadinessFinding(
            code="FINAL_NATIVE_CONTAINMENT_NOT_CERTIFIED",
            severity="HIGH",
            status="BLOCK",
            message="Hostile native-code containment is not certified for any approved production profile.",
        ))

    status=manifest.get("status")
    if status=="PRODUCTION_RELEASED":
        if manifest.get("production_ready") is not True:
            findings.append(ProductionReadinessFinding(
                code="RELEASED_WITHOUT_PRODUCTION_READY",
                severity="CRITICAL",
                status="BLOCK",
                message="PRODUCTION_RELEASED requires production_ready=true.",
            ))
        final_release=manifest.get("final_production_release") or {}
        if final_release.get("status")!="PASS":
            findings.append(ProductionReadinessFinding(
                code="FINAL_RELEASE_NOT_PASS",
                severity="CRITICAL",
                status="BLOCK",
                message="Production release evidence is not PASS.",
            ))
        profiles=set(manifest.get("approved_execution_profiles") or [])
        if "DOCKER_CONTAINED_ONLY" not in profiles:
            findings.append(ProductionReadinessFinding(
                code="APPROVED_PRODUCTION_PROFILE_MISSING",
                severity="CRITICAL",
                status="BLOCK",
                message="Released state requires DOCKER_CONTAINED_ONLY profile.",
            ))
    elif manifest.get("production_ready") is not False:
        findings.append(ProductionReadinessFinding(
            code="PREMATURE_PRODUCTION_READY",
            severity="CRITICAL",
            status="BLOCK",
            message="production_ready must remain false before final release.",
        ))

    return findings


def production_readiness_decision(root: str | Path) -> str:
    return "PASS" if not review_production_readiness(root) else "BLOCKED"
