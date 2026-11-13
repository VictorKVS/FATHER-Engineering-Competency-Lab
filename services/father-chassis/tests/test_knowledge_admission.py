from father.engineering.factory_agents import build_factory_agent_catalog
from father.engineering.knowledge_admission import (
    InMemoryKnowledgeReleaseRegistry,
    KnowledgeAdmissionRequest,
    KnowledgeBaseRelease,
    QualifiedKnowledgeAdmissionGate,
)


def _release(kb_id="KB-BUSINESS-ANALYSIS", status="QUALIFIED", provenance=True, retrieval=True):
    return KnowledgeBaseRelease(
        release_id=f"REL-{kb_id}-001",
        kb_id=kb_id,
        version="1.0.0",
        release_hash="a" * 64,
        status=status,
        source_set_hashes=("b" * 64,),
        provenance_refs=("provenance://1",) if provenance else (),
        retrieval_evidence_refs=("evidence://retrieval-1",) if retrieval else (),
        retrieval_metrics={"recall_at_5": 0.9} if retrieval else {},
        created_at="2026-11-13T00:00:00+00:00",
    )


def _gate(*releases):
    return QualifiedKnowledgeAdmissionGate(
        catalog=build_factory_agent_catalog(),
        registry=InMemoryKnowledgeReleaseRegistry(tuple(releases)),
    )


def test_qualified_required_release_is_admitted_with_trace():
    result = _gate(_release()).evaluate(
        KnowledgeAdmissionRequest(
            "WF-1",
            "BUSINESS_ANALYSIS",
            "FTH-AGENT-BUSINESS-ANALYST",
        )
    )
    assert result.admitted is True
    assert result.release_ids == ("REL-KB-BUSINESS-ANALYSIS-001",)
    assert result.release_hashes == ("a" * 64,)
    assert "provenance://1" in result.evidence_refs
    assert "evidence://retrieval-1" in result.evidence_refs


def test_missing_required_release_is_blocked():
    result = _gate().evaluate(
        KnowledgeAdmissionRequest(
            "WF-1",
            "BUSINESS_ANALYSIS",
            "FTH-AGENT-BUSINESS-ANALYST",
        )
    )
    assert result.admitted is False
    assert "missing qualified knowledge release" in result.reasons[0]


def test_unqualified_release_is_blocked():
    result = _gate(_release(status="DRAFT")).evaluate(
        KnowledgeAdmissionRequest(
            "WF-1",
            "BUSINESS_ANALYSIS",
            "FTH-AGENT-BUSINESS-ANALYST",
        )
    )
    assert result.admitted is False
    assert any("not QUALIFIED" in reason for reason in result.reasons)


def test_release_without_provenance_is_blocked():
    result = _gate(_release(provenance=False)).evaluate(
        KnowledgeAdmissionRequest(
            "WF-1",
            "BUSINESS_ANALYSIS",
            "FTH-AGENT-BUSINESS-ANALYST",
        )
    )
    assert result.admitted is False
    assert any("provenance_refs are required" in reason for reason in result.reasons)


def test_release_without_retrieval_evidence_is_blocked():
    result = _gate(_release(retrieval=False)).evaluate(
        KnowledgeAdmissionRequest(
            "WF-1",
            "BUSINESS_ANALYSIS",
            "FTH-AGENT-BUSINESS-ANALYST",
        )
    )
    assert result.admitted is False
    assert any("retrieval_evidence_refs are required" in reason for reason in result.reasons)


def test_duplicate_active_release_for_same_kb_is_rejected():
    import pytest

    with pytest.raises(ValueError, match="duplicate active knowledge release"):
        InMemoryKnowledgeReleaseRegistry((_release(), _release()))
