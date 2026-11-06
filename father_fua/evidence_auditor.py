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
    "factory/evidence/EVID-FUA-OLLAMA-0005.md",
    "factory/evidence/EVID-FUA-REALMODEL-PREFLIGHT-0006.md",
    "factory/evidence/EVID-FUA-REALMODEL-0007.md",
    "factory/evidence/EVID-FUA-REALMODEL-BENCH-0008.md",
    "factory/evidence/EVID-FUA-REALMODEL-POLYGON-0009.md",
    "factory/evidence/EVID-FUA-SANDBOX-EVM-0010.md",
    "factory/evidence/EVID-FUA-NETWORK-EVM-0011.md",
    "factory/evidence/EVID-FUA-FILESYSTEM-ACL-EVM-0012.md",
    "factory/evidence/EVID-FUA-RESTRICTED-TRUSTLEVEL-EVM-0013.md",
    "factory/evidence/EVID-FUA-FULL-POLYGON-REAL-RUNTIME-0014.md",
    "factory/evidence/EVID-FUA-FINAL-EVIDENCE-AUDIT-0015.md",
    "factory/evidence/EVID-FUA-RELIABILITY-GATE-EVM-0016.md",
    "factory/evidence/EVID-FUA-SANDBOX-STRESS-EVM-0017.md",
    "factory/evidence/EVID-FUA-FAULT-RECOVERY-STRESS-EVM-0018.md",
    "factory/evidence/EVID-FUA-INSTALLATION-TO-TESTING-0019.md",
)

REQUIRED_RUNTIME_FILES = (
    "father_fua/full_assembly.py",
    "father_fua/real_model_runtime.py",
    "father_fua/security_layer.py",
    "father_fua/evidence.py",
    "father_fua/sandbox.py",
    "father_fua/process_sandbox.py",
    "father_fua/real_runtime_polygon.py",
    "father_fua/human_acceptance.py",
    "father_fua/installation_gate.py",
)

REQUIRED_TEST_FILES = (
    "tests/test_full_assembly.py",
    "tests/test_polygon_lite.py",
    "tests/test_redteam_lite.py",
    "tests/test_api_negative.py",
    "tests/test_process_sandbox.py",
    "tests/test_real_model_contract.py",
    "tests/test_real_runtime_polygon.py",
    "tests/test_human_acceptance.py",
    "tests/test_installation_gate.py",
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

    status = manifest.get("status")
    permit = manifest.get("installation_permit")
    production_phase = status == "PRODUCTION_RELEASED"
    testing_phase = status in {
        "INSTALLATION_APPROVED_FOR_TESTING",
        "PRODUCT_TEST_IN_PROGRESS",
        "PRODUCT_TEST_VALIDATED",
        "PILOT_TEST_IN_PROGRESS",
        "PILOT_TEST_VALIDATED",
        "PRODUCTION_READINESS_REVIEW",
    }

    if production_phase:
        if manifest.get("production_ready") is not True:
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "PRODUCTION_RELEASE_WITHOUT_READY_STATE",
                    "PRODUCTION_RELEASED requires production_ready=true",
                )
            )
        if permit != "PASS":
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "PRODUCTION_RELEASE_WITHOUT_INSTALLATION_PERMIT",
                    f"status={status} permit={permit}",
                )
            )
        final_release = manifest.get("final_production_release") or {}
        if final_release.get("status") != "PASS":
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "FINAL_RELEASE_NOT_PROVEN",
                    str(final_release.get("status")),
                )
            )
        profiles = set(manifest.get("approved_execution_profiles") or [])
        if "DOCKER_CONTAINED_ONLY" not in profiles:
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "PRODUCTION_PROFILE_NOT_APPROVED",
                    str(sorted(profiles)),
                )
            )
        if manifest.get("windows_host_native_execution") != "NOT_APPROVED":
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "WINDOWS_NATIVE_POLICY_INVALID",
                    str(manifest.get("windows_host_native_execution")),
                )
            )
    elif testing_phase:
        if manifest.get("production_ready") is not False:
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "PREMATURE_PRODUCTION_READY",
                    "production_ready must remain false before final production release",
                )
            )
        if permit != "PASS":
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "TESTING_PHASE_WITHOUT_INSTALLATION_PERMIT",
                    f"status={status} permit={permit}",
                )
            )
        human = manifest.get("human_acceptance") or {}
        if human.get("status") != "PASS":
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "TESTING_PHASE_WITHOUT_HUMAN_ACCEPTANCE",
                    str(human.get("status")),
                )
            )
        install = manifest.get("installation_gate") or {}
        if install.get("status") != "PASS":
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "TESTING_PHASE_WITHOUT_INSTALLATION_GATE",
                    str(install.get("status")),
                )
            )
    else:
        if manifest.get("production_ready") is not False:
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "PREMATURE_PRODUCTION_READY",
                    "production_ready must remain false before controlled testing",
                )
            )
        if permit != "DENIED":
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "PREMATURE_INSTALLATION_PERMIT",
                    "installation permit must remain DENIED before controlled-testing approval",
                )
            )

    local=manifest.get("local_evm_evidence") or {}
    if local.get("full_01_26_assembly") != "PASS":
        findings.append(AuditFinding("HIGH","LOCAL_ASSEMBLY_NOT_PROVEN","local full assembly not proven"))


    required_target_gates = {
        "real_model_preflight": "PASS",
        "real_model_mission": "PASS",
        "real_model_benchmark": "PASS",
        "real_model_polygon": "PASS",
        "process_sandbox_evm": "PASS",
        "network_isolation_evm": "PASS",
        "filesystem_acl_evm": "PASS",
        "full_polygon_real_runtime": "PASS",
        "reliability_gate_evm": "PASS",
        "sandbox_stress_evm": "PASS",
        "fault_recovery_stress_evm": "PASS",
    }
    for key, expected in required_target_gates.items():
        actual = (manifest.get(key) or {}).get("status")
        if actual != expected:
            findings.append(
                AuditFinding(
                    "HIGH",
                    "TARGET_EVM_GATE_NOT_PASS",
                    f"{key}: expected {expected}, got {actual}",
                )
            )

    restricted = manifest.get("restricted_trustlevel_evm") or {}
    if restricted.get("status") not in {"PASS", "BLOCKED_BY_OS_CAPABILITY"}:
        findings.append(
            AuditFinding(
                "HIGH",
                "RESTRICTED_TRUSTLEVEL_STATE_INVALID",
                str(restricted.get("status")),
            )
        )
    if restricted.get("status") == "BLOCKED_BY_OS_CAPABILITY":
        if restricted.get("counted_as_pass") is not False:
            findings.append(
                AuditFinding(
                    "CRITICAL",
                    "BLOCKED_GATE_MISREPRESENTED_AS_PASS",
                    "restricted trustlevel blocked state must not count as PASS",
                )
            )

    full_polygon = manifest.get("full_polygon_real_runtime") or {}
    if full_polygon.get("side_effects") != 0:
        findings.append(
            AuditFinding(
                "CRITICAL",
                "POLYGON_SIDE_EFFECT_DETECTED",
                f"side_effects={full_polygon.get('side_effects')}",
            )
        )
    if full_polygon.get("scenario_count") != full_polygon.get("pass_count"):
        findings.append(
            AuditFinding(
                "HIGH",
                "POLYGON_SCENARIO_FAILURE",
                f"pass_count={full_polygon.get('pass_count')} scenario_count={full_polygon.get('scenario_count')}",
            )
        )

    next_gates = manifest.get("next_factory_gates") or []
    if production_phase:
        if next_gates:
            findings.append(
                AuditFinding(
                    "HIGH",
                    "PRODUCTION_RELEASE_HAS_PENDING_FACTORY_GATES",
                    f"next_factory_gates={next_gates}",
                )
            )
    elif testing_phase:
        expected_next_by_status = {
            "INSTALLATION_APPROVED_FOR_TESTING": {
                "PRODUCT_TEST",
                "PILOT_TEST",
                "PRODUCTION_READINESS_REVIEW",
            },
            "PRODUCT_TEST_IN_PROGRESS": {
                "PILOT_TEST",
                "PRODUCTION_READINESS_REVIEW",
            },
            "PRODUCT_TEST_VALIDATED": {
                "PILOT_TEST",
                "PRODUCTION_READINESS_REVIEW",
            },
            "PILOT_TEST_IN_PROGRESS": {
                "PRODUCTION_READINESS_REVIEW",
            },
            "PILOT_TEST_VALIDATED": {
                "PRODUCTION_READINESS_REVIEW",
            },
            "PRODUCTION_READINESS_REVIEW": set(),
        }
        required_next = expected_next_by_status.get(status, set())
        if not required_next.issubset(set(next_gates)):
            findings.append(
                AuditFinding(
                    "HIGH",
                    "TESTING_NEXT_GATES_INCOMPLETE",
                    f"status={status} next_factory_gates={next_gates} expected_at_least={sorted(required_next)}",
                )
            )
    else:
        if "HUMAN_ACCEPTANCE" not in next_gates:
            findings.append(
                AuditFinding(
                    "HIGH",
                    "HUMAN_ACCEPTANCE_NOT_PENDING",
                    "human acceptance must remain pending before release",
                )
            )

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
