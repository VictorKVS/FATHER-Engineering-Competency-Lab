from dataclasses import replace
from hashlib import sha256

from father.knowledge_factory.legal_provenance import (
    LegalAccessEvaluator,
    PolicyEvidence,
    SourceUsePolicy,
)
from father.knowledge_factory.source_intake import (
    InMemorySourceIntakeRegistry,
    SourceCandidate,
    SourceIntakeService,
)
from father.knowledge_factory.structural_parser import (
    DeterministicTextStructuralParser,
    StructuralParseRequest,
)


CONTENT = b"# TITLE\n\nFirst paragraph line one.\nline two.\n\nSECTION TWO\n\nSecond paragraph."


def _approved_request(content=CONTENT, media_type="text/markdown"):
    service = SourceIntakeService(InMemorySourceIntakeRegistry())
    intake = service.intake(
        SourceCandidate(
            source_id="SRC-SP-1",
            source_class="reference",
            title="Parser Source",
            locator="file:///knowledge/parser.md",
            version="1.0",
            content_bytes=content,
            declared_access="PUBLIC",
            declared_rights="DECLARED_PUBLIC",
        )
    ).record
    policy = SourceUsePolicy(
        policy_id="POL-SP-1",
        version="1.0.0",
        allowed_rights=frozenset({"DECLARED_PUBLIC"}),
        denied_rights=frozenset(),
        allowed_access=frozenset({"PUBLIC"}),
        required_evidence_types=frozenset({"rights_basis"}),
    )
    evidence = (
        PolicyEvidence(
            "EV-SP-1",
            "rights_basis",
            "owner",
            "evidence://sp/1",
            "a" * 64,
        ),
    )
    decision, provenance = LegalAccessEvaluator().evaluate(
        intake=intake,
        policy=policy,
        evidence=evidence,
    )
    assert decision.status == "APPROVED"
    return StructuralParseRequest(
        intake=intake,
        decision=decision,
        provenance=provenance,
        content_bytes=content,
        media_type=media_type,
    )


def test_approved_text_parses_with_order_and_locators():
    result = DeterministicTextStructuralParser().parse(_approved_request())
    assert result.status == "PARSED"
    assert result.document is not None
    assert [unit.unit_type for unit in result.document.units] == [
        "heading",
        "paragraph",
        "heading",
        "paragraph",
    ]
    assert [unit.ordinal for unit in result.document.units] == [0, 1, 2, 3]
    assert result.document.units[0].locator == "line:1-1"
    assert result.document.units[1].locator == "line:3-4"


def test_same_semantic_input_produces_same_document_hash_across_provenance_ids():
    parser = DeterministicTextStructuralParser()
    first_request = _approved_request()
    second_request = _approved_request()

    assert first_request.provenance.provenance_id != second_request.provenance.provenance_id

    first = parser.parse(first_request)
    second = parser.parse(second_request)

    assert first.document.document_hash == second.document.document_hash
    assert first.document.document_id == second.document.document_id
    assert first.document.provenance_id != second.document.provenance_id


def test_nonapproved_decision_is_rejected():
    request = _approved_request()
    request = replace(request, decision=replace(request.decision, status="HOLD"))
    result = DeterministicTextStructuralParser().parse(request)
    assert result.status == "REJECTED"
    assert result.document is None


def test_forged_provenance_is_rejected():
    request = _approved_request()
    forged = replace(request.provenance, source_content_hash="b" * 64)
    result = DeterministicTextStructuralParser().parse(
        replace(request, provenance=forged)
    )
    assert result.status == "REJECTED"
    assert any("provenance content_hash mismatch" in item for item in result.diagnostics)


def test_content_hash_mismatch_is_rejected():
    request = _approved_request()
    result = DeterministicTextStructuralParser().parse(
        replace(request, content_bytes=b"different")
    )
    assert result.status == "REJECTED"
    assert "content bytes do not match intake content_hash" in result.diagnostics


def test_invalid_utf8_is_rejected():
    content = b"\xff\xfe"
    request = _approved_request(content=content, media_type="text/plain")
    result = DeterministicTextStructuralParser().parse(request)
    assert result.status == "REJECTED"
    assert any("invalid UTF-8" in item for item in result.diagnostics)


def test_unsupported_media_type_is_rejected():
    result = DeterministicTextStructuralParser().parse(
        _approved_request(media_type="application/pdf")
    )
    assert result.status == "REJECTED"
    assert "unsupported media_type" in result.diagnostics[0]


def test_blank_input_is_rejected_explicitly():
    request = _approved_request(content=b"   \n\n", media_type="text/plain")
    result = DeterministicTextStructuralParser().parse(request)
    assert result.status == "REJECTED"
    assert result.diagnostics == ("source contains no structural text units",)


def test_every_unit_keeps_source_binding():
    request = _approved_request()
    result = DeterministicTextStructuralParser().parse(request)
    assert result.document.source_content_hash == sha256(CONTENT).hexdigest()
    for unit in result.document.units:
        assert unit.source_id == request.intake.source_id
        assert unit.source_content_hash == request.intake.content_hash
