from trust_competency.competency import CompetencyEvaluator, CompetencyPolicy
from trust_competency.models import Claim, EvidenceRecord


def _evidence(eid: str, evidence_type: str) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=eid,
        subject_id="SUB-1",
        claim_id="CLM-1",
        evidence_type=evidence_type,
        artifact_ref=eid + ".json",
        artifact_hash=eid,
        observed_at="2026-11-13T00:00:00+00:00",
        issuer="test",
    )


def test_product_and_person_use_same_evidence_policy_engine():
    claim = Claim("CLM-1", "SUB-1", "ai_architecture", "system_design", "C5")
    evidence = (
        _evidence("E1", "implementation"),
        _evidence("E2", "qualification"),
    )
    policy = CompetencyPolicy(
        level="C5",
        minimum_evidence_count=2,
        required_evidence_types=frozenset({"implementation", "qualification"}),
    )

    result = CompetencyEvaluator().qualify(
        claim=claim,
        evidence=evidence,
        policy=policy,
    )

    assert result.qualified is True


def test_missing_required_evidence_fails_closed():
    claim = Claim("CLM-1", "SUB-1", "ai_architecture", "system_design", "C5")
    policy = CompetencyPolicy(
        level="C5",
        minimum_evidence_count=2,
        required_evidence_types=frozenset({"implementation", "qualification"}),
    )

    result = CompetencyEvaluator().qualify(
        claim=claim,
        evidence=(_evidence("E1", "implementation"),),
        policy=policy,
    )

    assert result.qualified is False
    assert result.reasons
