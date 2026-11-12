from father.core.decision_trace import (
    DecisionEvidence,
    DecisionOption,
    NormReference,
)
from father.domain.kii_trace import KII_STAGES, new_kii_decision


def test_kii_decision_trace_end_to_end():
    trace = new_kii_decision("Qualification object KII-TEST-001")

    trace.add_evidence(
        DecisionEvidence(
            evidence_id="ev-asset-001",
            source="asset-register",
            locator="asset/KII-TEST-001",
            content_hash="a" * 64,
            summary="Source asset inventory evidence",
        )
    )

    norm = NormReference(
        source_id="norm-test",
        title="Qualification normative source",
        requirement_id="REQ-001",
        locator="section/test",
        version="test-version",
    )

    s1 = trace.add_step(
        stage="OBJECT_IDENTIFICATION",
        actor_type="agent",
        actor_id="father-compliance",
        statement="Object identified for KII applicability assessment",
        evidence_ids=["ev-asset-001"],
        confidence=0.95,
    )

    s2 = trace.add_step(
        stage="APPLICABILITY_ANALYSIS",
        actor_type="agent",
        actor_id="father-compliance",
        statement="Requirement applicability evaluated against object facts",
        norm_refs=[norm],
        evidence_ids=["ev-asset-001"],
        input_step_ids=[s1.step_id],
        confidence=0.9,
    )

    options = [
        DecisionOption("opt-a", "Apply control set A", benefits=("coverage",), risks=("cost",)),
        DecisionOption("opt-b", "Do not apply", rejected_reason="insufficient coverage"),
    ]

    trace.add_step(
        stage="CONTROL_SELECTION",
        actor_type="human",
        actor_id="security-architect",
        statement="Control set selected from evaluated alternatives",
        norm_refs=[norm],
        evidence_ids=["ev-asset-001"],
        input_step_ids=[s2.step_id],
        options=options,
        selected_option_id="opt-a",
        requires_human_approval=True,
        approval_id="approval-001",
    )

    assert trace.verify_chain()
    assert trace.to_dict()["chain_valid"] is True
    assert set(step.stage for step in trace.steps).issubset(set(KII_STAGES))


def test_kii_trace_detects_chain_tampering():
    trace = new_kii_decision("tamper-check")
    step = trace.add_step(
        stage="OBJECT_IDENTIFICATION",
        actor_type="agent",
        actor_id="father",
        statement="original statement",
    )
    assert trace.verify_chain()
    step.statement = "tampered statement"
    assert not trace.verify_chain()
