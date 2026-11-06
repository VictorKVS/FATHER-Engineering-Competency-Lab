import json
from pathlib import Path

from father_fua.final_release_gate import evaluate_final_release


def test_current_repository_is_already_released():
    root=Path(".")
    manifest=json.loads(
        (root/"factory/chassis/FUA-001/manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["status"]=="PRODUCTION_RELEASED"
    assert manifest["production_ready"] is True
    assert "DOCKER_CONTAINED_ONLY" in manifest["approved_execution_profiles"]
    assert manifest["windows_host_native_execution"]=="NOT_APPROVED"

    decision=evaluate_final_release(root)
    assert decision.allowed is False
    assert "production readiness is not validated" in decision.reason
