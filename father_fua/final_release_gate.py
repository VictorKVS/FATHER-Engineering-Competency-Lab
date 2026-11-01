from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FinalReleaseDecision:
    allowed: bool
    reason: str


def evaluate_final_release(root: str | Path) -> FinalReleaseDecision:
    root=Path(root)
    manifest=json.loads(
        (root/"factory/chassis/FUA-001/manifest.json").read_text(encoding="utf-8")
    )

    if manifest.get("status") != "PRODUCTION_READINESS_VALIDATED":
        return FinalReleaseDecision(False, "production readiness is not validated")

    review=manifest.get("production_readiness_review") or {}
    if review.get("status") != "PASS" or review.get("finding_count") != 0:
        return FinalReleaseDecision(False, "production readiness review is not clean")

    profiles=set(manifest.get("approved_execution_profiles") or [])
    if "DOCKER_CONTAINED_ONLY" not in profiles:
        return FinalReleaseDecision(False, "Docker-contained profile is not approved")

    docker=manifest.get("docker_native_containment_evm") or {}
    if docker.get("status") != "PASS":
        return FinalReleaseDecision(False, "Docker containment evidence is not PASS")

    if manifest.get("windows_host_native_execution") != "NOT_APPROVED":
        return FinalReleaseDecision(False, "Windows-host native execution policy must remain NOT_APPROVED")

    if manifest.get("production_ready") is not False:
        return FinalReleaseDecision(False, "production_ready must be false before final human decision")

    return FinalReleaseDecision(True, "technical gates passed; final human release decision required")
