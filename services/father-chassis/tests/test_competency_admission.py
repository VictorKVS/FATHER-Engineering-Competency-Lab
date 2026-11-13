import pytest

trust_competency = pytest.importorskip("trust_competency")

from trust_competency import Claim, EvidenceRecord

from father.engineering.competency_admission import (
    CompetencyAdmissionGate,
    CompetencyAdmissionRequest,
    InMemoryTrustCompetencySource,
    StageCompetencyPolicy,
)


def _evidence(eid, agent_id, claim_id, evidence_type):
    return EvidenceRecord(
        evidence_id=eid,
        subject_id=agent_id,
        claim_id=claim_id,
        evidence_type=evidence_type,
        artifact_ref=f"{eid}.json",
        artifact_hash=eid,
        observed_at="2026-11-13T00:00:00+00:00",
        issuer="test",
    )


def _gate(level="C5", evidence_types=frozenset({"implementation", "qualification"})):
    policy = StageCompetencyPolicy(
        stage_id="ARCHITECTURE",
        domain="ai_architecture",
        capability="system_design",
        minimum_level=level,
        minimum_evidence_count=2,
        required_evidence_types=evidence_types,
    )
    return policy


def test_qualified_agent_is_admitted_with_trust_trace():
    claim = Claim(
        "CLM-ARCH-1",
        "FTH-AGENT-ARCHITECT",
        "ai_architecture",
        "system_design",
        "C5",
    )
    evidence = (
        _evidence("E1", claim.subject_id, claim.claim_id, "implementation"),
        _evidence("E2", claim.subject_id, claim.claim_id, "qualification"),
    )
    gate = CompetencyAdmissionGate(
        source=InMemoryTrustCompetencySource((claim,), evidence),
        policies=(_gate(),),
    )

    result = gate.evaluate(
        CompetencyAdmissionRequest("WF-1", "ARCHITECTURE", claim.subject_id)
    )

    assert result.admitted is True
    assert result.trust_qualification_id == "QUAL-CLM-ARCH-1-C5"
    assert result.evidence_ids == ("E1", "E2")
    assert result.reasons == ()


def test_agent_below_required_level_is_blocked():
    claim = Claim(
        "CLM-ARCH-2",
        "FTH-AGENT-ARCHITECT",
        "ai_architecture",
        "system_design",
        "C3",
    )
    evidence = (
        _evidence("E1", claim.subject_id, claim.claim_id, "implementation"),
        _evidence("E2", claim.subject_id, claim.claim_id, "qualification"),
    )
    gate = CompetencyAdmissionGate(
        source=InMemoryTrustCompetencySource((claim,), evidence),
        policies=(_gate(),),
    )
    result = gate.evaluate(
        CompetencyAdmissionRequest("WF-1", "ARCHITECTURE", claim.subject_id)
    )
    assert result.admitted is False
    assert any("below requested qualification" in reason for reason in result.reasons)


def test_missing_required_evidence_is_blocked():
    claim = Claim(
        "CLM-ARCH-3",
        "FTH-AGENT-ARCHITECT",
        "ai_architecture",
        "system_design",
        "C5",
    )
    evidence = (
        _evidence("E1", claim.subject_id, claim.claim_id, "implementation"),
    )
    gate = CompetencyAdmissionGate(
        source=InMemoryTrustCompetencySource((claim,), evidence),
        policies=(_gate(),),
    )
    result = gate.evaluate(
        CompetencyAdmissionRequest("WF-1", "ARCHITECTURE", claim.subject_id)
    )
    assert result.admitted is False
    assert result.reasons


def test_wrong_domain_or_capability_claim_is_not_used():
    claim = Claim(
        "CLM-WRONG",
        "FTH-AGENT-ARCHITECT",
        "software_engineering",
        "coding",
        "C6",
    )
    gate = CompetencyAdmissionGate(
        source=InMemoryTrustCompetencySource((claim,), ()),
        policies=(_gate(),),
    )
    result = gate.evaluate(
        CompetencyAdmissionRequest("WF-1", "ARCHITECTURE", claim.subject_id)
    )
    assert result.admitted is False
    assert "no competency claim" in result.reasons[0]


def test_unknown_stage_policy_is_blocked():
    gate = CompetencyAdmissionGate(
        source=InMemoryTrustCompetencySource(),
        policies=(_gate(),),
    )
    result = gate.evaluate(
        CompetencyAdmissionRequest("WF-1", "UNKNOWN_STAGE", "AGENT")
    )
    assert result.admitted is False
    assert result.requested_level == "UNKNOWN"
