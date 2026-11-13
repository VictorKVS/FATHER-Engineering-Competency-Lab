from dataclasses import FrozenInstanceError
from hashlib import sha256

import pytest

from father.knowledge_factory.source_intake import (
    InMemorySourceIntakeRegistry,
    SourceCandidate,
    SourceIntakeService,
)


def _candidate(**overrides):
    values = {
        "source_id": "SRC-1",
        "source_class": "architecture_standard",
        "title": "Architecture Standard",
        "locator": "file:///knowledge/architecture-standard.pdf",
        "version": "1.0",
        "content_bytes": b"knowledge-source",
        "declared_access": "LOCAL_FILE",
        "declared_rights": "DECLARED_OWNED_COPY",
    }
    values.update(overrides)
    return SourceCandidate(**values)


def test_valid_source_is_fingerprinted_deterministically():
    service = SourceIntakeService(InMemorySourceIntakeRegistry())
    decision = service.intake(_candidate())

    assert decision.accepted is True
    assert decision.record is not None
    assert decision.record.content_hash == sha256(b"knowledge-source").hexdigest()
    assert decision.record.hash_algorithm == "sha256"
    assert decision.record.status == "INTAKE_READY"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("source_class", "  ", "source_class is required"),
        ("title", "", "title is required"),
        ("locator", " ", "locator is required"),
    ],
)
def test_required_metadata_is_enforced(field, value, message):
    service = SourceIntakeService(InMemorySourceIntakeRegistry())
    decision = service.intake(_candidate(**{field: value}))

    assert decision.accepted is False
    assert decision.record is None
    assert decision.reasons == (message,)


def test_duplicate_content_is_signalled_without_silent_merge():
    registry = InMemorySourceIntakeRegistry()
    service = SourceIntakeService(registry)

    first = service.intake(_candidate(source_id="SRC-1", title="First"))
    second = service.intake(_candidate(source_id="SRC-2", title="Second"))

    assert first.accepted is True
    assert second.accepted is True
    assert second.record is not None
    assert second.record.duplicate_of_source_id == "SRC-1"
    assert second.record.title == "Second"
    assert registry.get("SRC-1").title == "First"


def test_changed_bytes_under_same_locator_produce_different_hash():
    registry = InMemorySourceIntakeRegistry()
    service = SourceIntakeService(registry)

    first = service.intake(_candidate(source_id="SRC-1", content_bytes=b"v1"))
    second = service.intake(_candidate(source_id="SRC-2", content_bytes=b"v2"))

    assert first.record.content_hash != second.record.content_hash
    assert second.record.duplicate_of_source_id is None


def test_declared_rights_are_not_legal_approval():
    service = SourceIntakeService(InMemorySourceIntakeRegistry())
    decision = service.intake(_candidate(declared_rights="DECLARED_PUBLIC"))

    assert decision.record.declared_rights == "DECLARED_PUBLIC"
    assert "LEGAL_APPROVED" not in decision.record.declared_rights
    assert decision.record.status == "INTAKE_READY"


def test_intake_record_is_immutable():
    service = SourceIntakeService(InMemorySourceIntakeRegistry())
    record = service.intake(_candidate()).record

    with pytest.raises(FrozenInstanceError):
        record.title = "mutated"


def test_duplicate_source_id_is_rejected():
    registry = InMemorySourceIntakeRegistry()
    service = SourceIntakeService(registry)

    assert service.intake(_candidate()).accepted is True
    second = service.intake(_candidate(content_bytes=b"other"))

    assert second.accepted is False
    assert second.record is None
    assert "duplicate source_id" in second.reasons[0]


def test_missing_bytes_is_allowed_but_not_falsely_fingerprinted():
    service = SourceIntakeService(InMemorySourceIntakeRegistry())
    decision = service.intake(_candidate(content_bytes=None))

    assert decision.accepted is True
    assert decision.record.content_hash is None
    assert decision.record.hash_algorithm is None
    assert decision.evidence_refs == ()
