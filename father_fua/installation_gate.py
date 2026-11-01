from __future__ import annotations

from dataclasses import dataclass

from father_fua.human_acceptance import HumanAcceptance, verify_human_acceptance
from father_fua.readiness import release_decision, MANDATORY


@dataclass(frozen=True)
class InstallationDecision:
    decision: str
    reason: str
    gates: dict[str, str]


def evaluate_installation_gate(
    *,
    current_snapshot_sha256: str,
    acceptance: HumanAcceptance | None,
    automated_gates: dict[str, str],
) -> InstallationDecision:
    gates={name: automated_gates.get(name,"NOT_RUN") for name in MANDATORY}

    if acceptance is None:
        gates["HUMAN_ACCEPTANCE"]="NOT_RUN"
        return InstallationDecision(
            "DENIED",
            "human acceptance missing",
            gates,
        )

    accepted=verify_human_acceptance(
        acceptance,
        current_snapshot_sha256=current_snapshot_sha256,
    )
    gates["HUMAN_ACCEPTANCE"]="PASS" if accepted else "FAIL"

    decision=release_decision(gates)
    if decision!="PASS":
        return InstallationDecision(
            "DENIED",
            "one or more mandatory gates are not PASS",
            gates,
        )

    return InstallationDecision("PASS","all mandatory gates passed",gates)
