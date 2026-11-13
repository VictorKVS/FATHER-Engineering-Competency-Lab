import pytest

from father.engineering.delivery_contract import (
    AcceptanceCriterion,
    AlgorithmSpec,
    ArchitectureSpec,
    BusinessProcessSpec,
    DevelopmentPacketBuilder,
    InterfaceContract,
    TestContract as EngineeringTestContract,
    VariableContract,
)
from father.engineering.factory_orchestrator import FactoryEngineeringWorkflow, StageArtifact
from father.engineering.stage_artifacts import (
    CustomerRequestPayload,
    DeliveryQualification,
    ImplementationChange,
    QualificationDecision,
    SystemAnalysisPackage,
)


def _payload(artifact_type):
    if artifact_type == "customer_request":
        return CustomerRequestPayload("REQ-TEST", "Test request", "Exercise workflow")
    if artifact_type == "BusinessProcessSpec":
        return BusinessProcessSpec(
            process_id="BP-TEST",
            goal="exercise workflow",
            inputs=("request",),
            outputs=("analysis",),
            actors=("factory",),
            approved=True,
        )
    if artifact_type == "SystemAnalysisPackage":
        return SystemAnalysisPackage(
            analysis_id="SYS-TEST",
            functional_requirements=("FR-1",),
            nonfunctional_requirements=("NFR-1",),
            states=("READY",),
            events=("START",),
            data_entities=("Artifact",),
            interfaces=("IF-1",),
            failure_modes=("invalid",),
            approved=True,
        )
    if artifact_type == "AlgorithmSpec":
        return AlgorithmSpec(
            algorithm_id="ALG-TEST",
            process_id="BP-TEST",
            preconditions=("ready",),
            steps=("execute",),
            postconditions=("done",),
            approved=True,
        )
    if artifact_type == "ArchitectureSpec":
        return ArchitectureSpec(
            architecture_id="ARCH-TEST",
            algorithm_id="ALG-TEST",
            blocks=("A", "B"),
            interfaces=(
                InterfaceContract(
                    "IF-TEST",
                    "A",
                    "B",
                    (VariableContract("x", "str", "A", "input"),),
                    (),
                ),
            ),
            states=("READY",),
            approved=True,
        )
    if artifact_type == "TestContract":
        return EngineeringTestContract(
            test_contract_id="TEST-TEST",
            architecture_id="ARCH-TEST",
            criteria=(
                AcceptanceCriterion("AC-1", "works", "success", "==", 1, "unit"),
            ),
            approved=True,
        )
    if artifact_type == "DevelopmentPacket":
        return DevelopmentPacketBuilder.build(
            packet_id="DEV-TEST",
            business_process=_payload("BusinessProcessSpec"),
            algorithm=_payload("AlgorithmSpec"),
            architecture=_payload("ArchitectureSpec"),
            test_contract=_payload("TestContract"),
            system_analysis_approved=True,
        )
    if artifact_type == "ImplementationChange":
        return ImplementationChange("CHG-1", ("file.py",), ("DEV-TEST",), ("pytest",))
    if artifact_type == "DeliveryQualification":
        return DeliveryQualification(
            "DELIV-1",
            "build://1",
            "deploy://1",
            ("sec://1",),
            ("obs://1",),
            ("rollback://1",),
        )
    if artifact_type == "QualificationDecision":
        return QualificationDecision(
            "QUAL-1",
            "PASS",
            ("AC-1=PASS",),
            ("evidence://1",),
        )
    raise AssertionError(f"unsupported test artifact_type {artifact_type}")


def _artifact(artifact_id, artifact_type, producer, approved=True):
    return StageArtifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        producer_agent_id=producer,
        payload=_payload(artifact_type),
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


def test_workflow_persists_and_restores_next_stage(tmp_path):
    from father.core.state import SQLiteStateStore

    store = SQLiteStateStore(tmp_path / "workflow.db")
    first = FactoryEngineeringWorkflow(store=store, workflow_id="WF-PERSIST-1")
    first.add_external_artifact(
        _artifact("REQ-PERSIST", "customer_request", "HUMAN_APPROVAL")
    )
    assert first.available_stage().stage_id == "BUSINESS_ANALYSIS"

    first.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        _artifact(
            "BP-PERSIST",
            "BusinessProcessSpec",
            "FTH-AGENT-BUSINESS-ANALYST",
        ),
    )
    assert first.available_stage().stage_id == "SYSTEM_ANALYSIS"

    second = FactoryEngineeringWorkflow(store=store, workflow_id="WF-PERSIST-1")

    assert second.available_stage().stage_id == "SYSTEM_ANALYSIS"
    assert second.status()["completed_stages"] == ["BUSINESS_ANALYSIS"]
    assert second.status()["artifacts"]["BusinessProcessSpec"]["artifact_id"] == "BP-PERSIST"


def test_workflow_ids_are_isolated(tmp_path):
    from father.core.state import SQLiteStateStore

    store = SQLiteStateStore(tmp_path / "workflow.db")
    first = FactoryEngineeringWorkflow(store=store, workflow_id="WF-A")
    first.add_external_artifact(
        _artifact("REQ-A", "customer_request", "HUMAN_APPROVAL")
    )

    second = FactoryEngineeringWorkflow(store=store, workflow_id="WF-B")

    assert second.available_stage() is None
    assert second.status()["artifacts"] == {}


def test_workflow_restore_rejects_tampered_artifact_hash(tmp_path):
    from father.core.state import SQLiteStateStore

    store = SQLiteStateStore(tmp_path / "workflow.db")
    workflow = FactoryEngineeringWorkflow(store=store, workflow_id="WF-TAMPER")
    workflow.add_external_artifact(
        _artifact("REQ-TAMPER", "customer_request", "HUMAN_APPROVAL")
    )

    snapshot = store.get(FactoryEngineeringWorkflow.NAMESPACE, "WF-TAMPER")
    snapshot["artifacts"]["customer_request"]["payload_data"]["objective"] = "tampered"
    store.set(FactoryEngineeringWorkflow.NAMESPACE, "WF-TAMPER", snapshot)

    with pytest.raises(ValueError, match="stage artifact hash mismatch"):
        FactoryEngineeringWorkflow(store=store, workflow_id="WF-TAMPER")


def test_blocked_history_survives_restart(tmp_path):
    from father.core.state import SQLiteStateStore

    store = SQLiteStateStore(tmp_path / "workflow.db")
    first = FactoryEngineeringWorkflow(store=store, workflow_id="WF-BLOCKED")
    first.add_external_artifact(
        _artifact("REQ-B", "customer_request", "HUMAN_APPROVAL")
    )
    blocked = first.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        _artifact(
            "BP-WRONG",
            "BusinessProcessSpec",
            "FTH-AGENT-SENIOR-DEVELOPER",
        ),
    )
    assert blocked.status == "BLOCKED"

    second = FactoryEngineeringWorkflow(store=store, workflow_id="WF-BLOCKED")
    assert second.status()["history"][-1]["status"] == "BLOCKED"
    assert second.available_stage().stage_id == "BUSINESS_ANALYSIS"


def test_legacy_workflow_snapshot_schema_is_rejected(tmp_path):
    from father.core.state import SQLiteStateStore

    store = SQLiteStateStore(tmp_path / "workflow.db")
    store.set(
        FactoryEngineeringWorkflow.NAMESPACE,
        "WF-LEGACY",
        {
            "schema_version": 1,
            "workflow_id": "WF-LEGACY",
            "artifacts": {},
            "history": [],
        },
    )

    with pytest.raises(
        ValueError,
        match="unsupported factory engineering workflow snapshot schema",
    ):
        FactoryEngineeringWorkflow(store=store, workflow_id="WF-LEGACY")


def test_required_competency_gate_blocks_underqualified_stage():
    trust_competency = pytest.importorskip("trust_competency")
    from trust_competency import Claim, EvidenceRecord

    from father.engineering.competency_admission import (
        CompetencyAdmissionGate,
        InMemoryTrustCompetencySource,
        StageCompetencyPolicy,
    )

    claim = Claim(
        "CLM-BA",
        "FTH-AGENT-BUSINESS-ANALYST",
        "business_analysis",
        "process_design",
        "C1",
    )
    evidence = (
        EvidenceRecord(
            "E1",
            claim.subject_id,
            claim.claim_id,
            "implementation",
            "E1.json",
            "E1",
            "2026-11-13T00:00:00+00:00",
            "test",
        ),
        EvidenceRecord(
            "E2",
            claim.subject_id,
            claim.claim_id,
            "qualification",
            "E2.json",
            "E2",
            "2026-11-13T00:00:00+00:00",
            "test",
        ),
    )
    gate = CompetencyAdmissionGate(
        source=InMemoryTrustCompetencySource((claim,), evidence),
        policies=(
            StageCompetencyPolicy(
                "BUSINESS_ANALYSIS",
                "business_analysis",
                "process_design",
                "C3",
                2,
                frozenset({"implementation", "qualification"}),
            ),
        ),
    )
    workflow = FactoryEngineeringWorkflow(
        competency_gate=gate,
        require_competency_admission=True,
    )
    workflow.add_external_artifact(
        _artifact("REQ-COMP", "customer_request", "HUMAN_APPROVAL")
    )

    result = workflow.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        _artifact(
            "BP-COMP",
            "BusinessProcessSpec",
            "FTH-AGENT-BUSINESS-ANALYST",
        ),
    )

    assert result.status == "BLOCKED"
    assert result.competency_qualification_id == "QUAL-CLM-BA-C3"
    assert result.competency_evidence_ids == ("E1", "E2")
    assert any("competency admission:" in item for item in result.blocking_findings)


def test_required_competency_gate_allows_qualified_stage():
    trust_competency = pytest.importorskip("trust_competency")
    from trust_competency import Claim, EvidenceRecord

    from father.engineering.competency_admission import (
        CompetencyAdmissionGate,
        InMemoryTrustCompetencySource,
        StageCompetencyPolicy,
    )

    claim = Claim(
        "CLM-BA-Q",
        "FTH-AGENT-BUSINESS-ANALYST",
        "business_analysis",
        "process_design",
        "C3",
    )
    evidence = tuple(
        EvidenceRecord(
            eid,
            claim.subject_id,
            claim.claim_id,
            evidence_type,
            f"{eid}.json",
            eid,
            "2026-11-13T00:00:00+00:00",
            "test",
        )
        for eid, evidence_type in (
            ("E1", "implementation"),
            ("E2", "qualification"),
        )
    )
    gate = CompetencyAdmissionGate(
        source=InMemoryTrustCompetencySource((claim,), evidence),
        policies=(
            StageCompetencyPolicy(
                "BUSINESS_ANALYSIS",
                "business_analysis",
                "process_design",
                "C3",
                2,
                frozenset({"implementation", "qualification"}),
            ),
        ),
    )
    workflow = FactoryEngineeringWorkflow(
        competency_gate=gate,
        require_competency_admission=True,
    )
    workflow.add_external_artifact(
        _artifact("REQ-COMP-Q", "customer_request", "HUMAN_APPROVAL")
    )

    result = workflow.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        _artifact(
            "BP-COMP-Q",
            "BusinessProcessSpec",
            "FTH-AGENT-BUSINESS-ANALYST",
        ),
    )

    assert result.status == "PASS"
    assert result.competency_qualification_id == "QUAL-CLM-BA-Q-C3"
    assert result.competency_evidence_ids == ("E1", "E2")


def test_required_competency_mode_without_gate_fails_closed():
    with pytest.raises(
        ValueError,
        match="competency admission is required but no competency_gate is configured",
    ):
        FactoryEngineeringWorkflow(require_competency_admission=True)


def test_snapshot_v2_is_rejected_after_competency_history_contract_change(tmp_path):
    from father.core.state import SQLiteStateStore

    store = SQLiteStateStore(tmp_path / "workflow.db")
    store.set(
        FactoryEngineeringWorkflow.NAMESPACE,
        "WF-V2",
        {
            "schema_version": 2,
            "workflow_id": "WF-V2",
            "artifacts": {},
            "history": [],
        },
    )
    with pytest.raises(
        ValueError,
        match="unsupported factory engineering workflow snapshot schema",
    ):
        FactoryEngineeringWorkflow(store=store, workflow_id="WF-V2")


def _qualified_business_kb_gate():
    from father.engineering.factory_agents import build_factory_agent_catalog
    from father.engineering.knowledge_admission import (
        InMemoryKnowledgeReleaseRegistry,
        KnowledgeBaseRelease,
        QualifiedKnowledgeAdmissionGate,
    )

    release = KnowledgeBaseRelease(
        release_id="REL-KB-BUSINESS-001",
        kb_id="KB-BUSINESS-ANALYSIS",
        version="1.0.0",
        release_hash="a" * 64,
        status="QUALIFIED",
        source_set_hashes=("b" * 64,),
        provenance_refs=("provenance://business",),
        retrieval_evidence_refs=("evidence://retrieval-business",),
        retrieval_metrics={"recall_at_5": 0.91},
        created_at="2026-11-13T00:00:00+00:00",
    )
    return QualifiedKnowledgeAdmissionGate(
        catalog=build_factory_agent_catalog(),
        registry=InMemoryKnowledgeReleaseRegistry((release,)),
    )


def test_required_knowledge_gate_allows_qualified_release():
    workflow = FactoryEngineeringWorkflow(
        knowledge_gate=_qualified_business_kb_gate(),
        require_knowledge_admission=True,
    )
    workflow.add_external_artifact(
        _artifact("REQ-KB", "customer_request", "HUMAN_APPROVAL")
    )

    result = workflow.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        _artifact(
            "BP-KB",
            "BusinessProcessSpec",
            "FTH-AGENT-BUSINESS-ANALYST",
        ),
    )

    assert result.status == "PASS"
    assert result.knowledge_release_ids == ("REL-KB-BUSINESS-001",)
    assert result.knowledge_release_hashes == ("a" * 64,)
    assert "evidence://retrieval-business" in result.knowledge_evidence_refs


def test_required_knowledge_gate_blocks_missing_release():
    from father.engineering.factory_agents import build_factory_agent_catalog
    from father.engineering.knowledge_admission import (
        InMemoryKnowledgeReleaseRegistry,
        QualifiedKnowledgeAdmissionGate,
    )

    gate = QualifiedKnowledgeAdmissionGate(
        catalog=build_factory_agent_catalog(),
        registry=InMemoryKnowledgeReleaseRegistry(),
    )
    workflow = FactoryEngineeringWorkflow(
        knowledge_gate=gate,
        require_knowledge_admission=True,
    )
    workflow.add_external_artifact(
        _artifact("REQ-KB-MISS", "customer_request", "HUMAN_APPROVAL")
    )

    result = workflow.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        _artifact(
            "BP-KB-MISS",
            "BusinessProcessSpec",
            "FTH-AGENT-BUSINESS-ANALYST",
        ),
    )

    assert result.status == "BLOCKED"
    assert any("knowledge admission:" in item for item in result.blocking_findings)


def test_required_knowledge_mode_without_gate_fails_closed():
    with pytest.raises(
        ValueError,
        match="knowledge admission is required but no knowledge_gate is configured",
    ):
        FactoryEngineeringWorkflow(require_knowledge_admission=True)


def test_snapshot_v3_is_rejected_after_knowledge_history_contract_change(tmp_path):
    from father.core.state import SQLiteStateStore

    store = SQLiteStateStore(tmp_path / "workflow.db")
    store.set(
        FactoryEngineeringWorkflow.NAMESPACE,
        "WF-V3",
        {
            "schema_version": 3,
            "workflow_id": "WF-V3",
            "artifacts": {},
            "history": [],
        },
    )
    with pytest.raises(
        ValueError,
        match="unsupported factory engineering workflow snapshot schema",
    ):
        FactoryEngineeringWorkflow(store=store, workflow_id="WF-V3")
