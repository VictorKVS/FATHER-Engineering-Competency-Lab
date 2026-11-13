from trust_competency.ledger import EvidenceLedger
from trust_competency.models import EvidenceRecord


def _record(evidence_id: str) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        subject_id="SUB-1",
        claim_id="CLM-1",
        evidence_type="test",
        artifact_ref="artifact.json",
        artifact_hash="abc123",
        observed_at="2026-11-13T00:00:00+00:00",
        issuer="test",
    )


def test_ledger_links_records_and_verifies_chain():
    ledger = EvidenceLedger()
    first = ledger.append(_record("EVD-1"))
    second = ledger.append(_record("EVD-2"))

    assert first.parent_evidence_hash is None
    assert second.parent_evidence_hash == first.record_hash
    assert ledger.verify() is True


def test_ledger_rejects_duplicate_evidence_id():
    ledger = EvidenceLedger()
    ledger.append(_record("EVD-1"))

    try:
        ledger.append(_record("EVD-1"))
    except ValueError as exc:
        assert "duplicate evidence_id" in str(exc)
    else:
        raise AssertionError("duplicate evidence ID must fail")
