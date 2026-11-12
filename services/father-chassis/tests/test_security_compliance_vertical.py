import pytest

from father.core.access_control import (
    AccessControl,
    ClearanceLevel,
    ResourceContext,
    SubjectContext,
)
from father.core.decision_trace import NormReference
from father.domain.kii_engine import KIIDecisionEngine


def _norm():
    return NormReference(
        source_id="qualification-norm",
        title="Qualification KII norm",
        requirement_id="REQ-KII-001",
        locator="qualification/1",
        version="1",
    )


def test_unauthorized_subject_cannot_create_kii_decision():
    engine = KIIDecisionEngine(AccessControl())
    subject = SubjectContext(
        subject_id="viewer-1",
        roles=frozenset({"viewer"}),
        clearance=ClearanceLevel.PUBLIC,
    )
    resource = ResourceContext(
        resource_id="kii-object",
        classification=ClearanceLevel.RESTRICTED,
        compartments=frozenset({"KII"}),
    )

    with pytest.raises(PermissionError):
        engine.assess(
            subject=subject,
            resource=resource,
            object_id="KII-001",
            object_facts="Qualification facts",
            norm=_norm(),
            proposed_decision="Continue KII assessment",
        )


def test_authorized_specialist_gets_sealed_decision_trace():
    engine = KIIDecisionEngine(AccessControl())
    subject = SubjectContext(
        subject_id="specialist-1",
        roles=frozenset({"security_specialist"}),
        clearance=ClearanceLevel.RESTRICTED,
        compartments=frozenset({"KII"}),
    )
    resource = ResourceContext(
        resource_id="kii-object",
        classification=ClearanceLevel.RESTRICTED,
        compartments=frozenset({"KII"}),
    )

    result = engine.assess(
        subject=subject,
        resource=resource,
        object_id="KII-001",
        object_facts="Qualification facts",
        norm=_norm(),
        proposed_decision="Continue KII assessment",
    )

    assert result["access"]["allowed"] is True
    assert result["access"]["matched_role"] == "security_specialist"
    assert result["decision_trace"]["chain_valid"] is True
    assert len(result["decision_trace"]["steps"]) == 4
    assert result["decision_trace"]["steps"][-1]["requires_human_approval"] is True
