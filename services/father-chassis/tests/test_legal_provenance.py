from dataclasses import replace

from father.knowledge_factory.legal_provenance import (
    LegalAccessEvaluator,
    PolicyEvidence,
    SourceUsePolicy,
    verify_provenance_binding,
)
from father.knowledge_factory.source_intake import (
    InMemorySourceIntakeRegistry,
    SourceCandidate,
    SourceIntakeService,
)


def _intake(rights="DECLARED_PUBLIC", access="PUBLIC"):
    service = SourceIntakeService(InMemorySourceIntakeRegistry())
    return service.intake(
        SourceCandidate(
            source_id="SRC-LP-1",
            source_class="architecture_standard",
            title="Architecture Standard",
            locator="file:///knowledge/source.pdf",
            version="1.0",
            content_bytes=b"source",
            declared_access=access,
            declared_rights=rights,
        )
    ).record


def _policy():
    return SourceUsePolicy(
        policy_id="POL-KB-SOURCE-1",
        version="1.0.0",
        allowed_rights=frozenset({"DECLARED_PUBLIC", "DECLARED_OWNED_COPY"}),
        denied_rights=frozenset({"DECLARED_DENIED"}),
        allowed_access=frozenset({"PUBLIC", "LOCAL_FILE"}),
        required_evidence_types=frozenset({"rights_basis"}),
        allowed_use=("knowledge_processing", "retrieval_indexing"),
    )


def _evidence():
    return (
        PolicyEvidence(
            evidence_id="EV-1",
            evidence_type="rights_basis",
            authority="owner",
            locator="evidence://rights/1",
            evidence_hash="a" * 64,
        ),
    )


def test_allowed_source_with_evidence_is_approved_and_bound():
    intake = _intake()
    decision, provenance = LegalAccessEvaluator().evaluate(
        intake=intake,
        policy=_policy(),
        evidence=_evidence(),
    )
    assert decision.status == "APPROVED"
    assert decision.allowed_use == ("knowledge_processing", "retrieval_indexing")
    assert verify_provenance_binding(intake, decision, provenance) == ()


def test_denied_right_is_rejected():
    decision, _ = LegalAccessEvaluator().evaluate(
        intake=_intake(rights="DECLARED_DENIED"),
        policy=_policy(),
        evidence=_evidence(),
    )
    assert decision.status == "REJECTED"


def test_unknown_right_is_held():
    decision, _ = LegalAccessEvaluator().evaluate(
        intake=_intake(rights="UNKNOWN"),
        policy=_policy(),
        evidence=_evidence(),
    )
    assert decision.status == "HOLD"


def test_missing_evidence_is_held():
    decision, _ = LegalAccessEvaluator().evaluate(
        intake=_intake(),
        policy=_policy(),
        evidence=(),
    )
    assert decision.status == "HOLD"
    assert any("missing required evidence types" in item for item in decision.reasons)


def test_disallowed_access_is_held():
    decision, _ = LegalAccessEvaluator().evaluate(
        intake=_intake(access="PRIVATE_REMOTE"),
        policy=_policy(),
        evidence=_evidence(),
    )
    assert decision.status == "HOLD"


def test_source_without_hash_is_not_approved():
    service = SourceIntakeService(InMemorySourceIntakeRegistry())
    intake = service.intake(
        SourceCandidate(
            source_id="SRC-NOHASH",
            source_class="reference",
            title="No hash",
            locator="https://example.invalid/source",
            content_bytes=None,
            declared_access="PUBLIC",
            declared_rights="DECLARED_PUBLIC",
        )
    ).record
    decision, _ = LegalAccessEvaluator().evaluate(
        intake=intake,
        policy=_policy(),
        evidence=_evidence(),
    )
    assert decision.status == "HOLD"


def test_provenance_hash_substitution_is_detected():
    intake = _intake()
    decision, provenance = LegalAccessEvaluator().evaluate(
        intake=intake,
        policy=_policy(),
        evidence=_evidence(),
    )
    forged = replace(provenance, source_content_hash="b" * 64)
    errors = verify_provenance_binding(intake, decision, forged)
    assert "provenance content_hash mismatch" in errors


def test_policy_id_and_version_are_preserved():
    decision, _ = LegalAccessEvaluator().evaluate(
        intake=_intake(),
        policy=_policy(),
        evidence=_evidence(),
    )
    assert decision.policy_id == "POL-KB-SOURCE-1"
    assert decision.policy_version == "1.0.0"
