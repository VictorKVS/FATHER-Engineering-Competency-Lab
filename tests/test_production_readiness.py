from pathlib import Path

from father_fua.production_readiness import production_readiness_decision, review_production_readiness


def test_current_repository_production_readiness_is_blocked():
    findings=review_production_readiness(Path("."))
    assert production_readiness_decision(Path("."))=="BLOCKED"
    codes={f.code for f in findings}
    assert "OS_TRUST_BOUNDARY_NOT_PROVEN" in codes
    assert "FINAL_NATIVE_CONTAINMENT_NOT_CERTIFIED" in codes
