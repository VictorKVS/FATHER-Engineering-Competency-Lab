import pytest

from father.engineering.factory_orchestrator import FactoryEngineeringWorkflow, StageArtifact


def _artifact(artifact_id, artifact_type, producer, approved=True):
    return StageArtifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        producer_agent_id=producer,
        payload={"artifact_type": artifact_type},
        approved=approved,
        evidence_refs=(f"evidence://{artifact_id}",),
    )


def test_workflow_starts_only_after_approved_customer_request():
    workflow = FactoryEngineeringWorkflow()
    assert workflow.available_stage() is None

    with pytest.raises(ValueError, match="external artifact must be approved"):
        workflow.add_external_artifact(
            _artifact("REQ-0", "customer_request", "HUMAN_APPROVAL", approved=False)
        )

    workflow.add_external_artifact(
        _artifact("REQ-1", "customer_request", "HUMAN_APPROVAL")
    )
    assert workflow.available_stage().stage_id == "BUSINESS_ANALYSIS"


def test_wrong_role_cannot_submit_stage_output():
    workflow = FactoryEngineeringWorkflow()
    workflow.add_external_artifact(
        _artifact("REQ-1", "customer_request", "HUMAN_APPROVAL")
    )

    result = workflow.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        _artifact(
            "BP-1",
            "BusinessProcessSpec",
            "FTH-AGENT-SENIOR-DEVELOPER",
        ),
    )

    assert result.status == "BLOCKED"
    assert "artifact producer does not own this stage" in result.blocking_findings


def test_developer_cannot_start_before_development_packet_exists():
    workflow = FactoryEngineeringWorkflow()
    workflow.add_external_artifact(
        _artifact("REQ-1", "customer_request", "HUMAN_APPROVAL")
    )

    with pytest.raises(ValueError, match="not currently executable"):
        workflow.submit_stage_artifact(
            "IMPLEMENTATION",
            _artifact(
                "IMPL-1",
                "ImplementationChange",
                "FTH-AGENT-SENIOR-DEVELOPER",
            ),
        )


def test_full_handoff_sequence_is_fail_closed_and_traceable():
    workflow = FactoryEngineeringWorkflow()
    workflow.add_external_artifact(
        _artifact("REQ-1", "customer_request", "HUMAN_APPROVAL")
    )

    sequence = [
        ("BUSINESS_ANALYSIS", "BP-1", "BusinessProcessSpec", "FTH-AGENT-BUSINESS-ANALYST"),
        ("SYSTEM_ANALYSIS", "SYS-1", "SystemAnalysisPackage", "FTH-AGENT-SYSTEM-ANALYST"),
        ("ALGORITHM_SELECTION", "ALG-1", "AlgorithmSpec", "FTH-AGENT-ALGORITHM-ENGINEER"),
        ("ARCHITECTURE", "ARCH-1", "ArchitectureSpec", "FTH-AGENT-ARCHITECT"),
        ("TEST_ARCHITECTURE", "TEST-1", "TestContract", "FTH-AGENT-TEST-ARCHITECT"),
        ("DEVELOPMENT_PACKET", "DEVPKG-1", "DevelopmentPacket", "FTH-AGENT-ARCHITECT"),
        ("IMPLEMENTATION", "IMPL-1", "ImplementationChange", "FTH-AGENT-SENIOR-DEVELOPER"),
        ("DELIVERY", "DELIV-1", "DeliveryQualification", "FTH-AGENT-DEVSECOPS"),
        ("QUALIFICATION", "QUAL-1", "QualificationDecision", "FTH-AGENT-QUALIFICATION-AUDITOR"),
    ]

    for stage_id, artifact_id, artifact_type, producer in sequence:
        assert workflow.available_stage().stage_id == stage_id
        result = workflow.submit_stage_artifact(
            stage_id,
            _artifact(artifact_id, artifact_type, producer),
        )
        assert result.status == "PASS"

    assert workflow.available_stage() is None
    status = workflow.status()
    assert status["completed_stages"] == [item[0] for item in sequence]
    assert status["artifacts"]["QualificationDecision"]["approved"] is True
    assert workflow.workflow_hash()
