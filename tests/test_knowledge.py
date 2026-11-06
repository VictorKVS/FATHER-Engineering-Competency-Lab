import pytest
from father_fua.knowledge import KnowledgeRegistry


def test_candidate_requires_provenance():
    k = KnowledgeRegistry()
    with pytest.raises(ValueError):
        k.register_candidate(
            knowledge_id="K1", term="Agent", definition="x",
            definition_type="EXPLICIT_SOURCE", provenance=[], confidence=0.9
        )


def test_candidate_can_be_canonicalized_only_after_approval():
    k = KnowledgeRegistry()
    k.register_candidate(
        knowledge_id="K1", term="Agent", definition="x",
        definition_type="EXPLICIT_SOURCE", provenance=["SRC-1"], confidence=0.9
    )
    with pytest.raises(PermissionError):
        k.canonicalize("K1", approved=False)
    item = k.canonicalize("K1", approved=True)
    assert item.canonical is True
    assert item.review_status == "VALIDATED"


def test_conflicting_definitions_are_preserved():
    k = KnowledgeRegistry()
    k.register_candidate(
        knowledge_id="K1", term="Agent", definition="definition A",
        definition_type="EXPLICIT_SOURCE", provenance=["SRC-A"], confidence=0.9
    )
    k.register_candidate(
        knowledge_id="K2", term="Agent", definition="definition B",
        definition_type="DISTRIBUTED_SOURCE", provenance=["SRC-B"], confidence=0.8
    )
    assert len(k.by_term("Agent")) == 2


def test_revoked_support_removes_canonical_status():
    k = KnowledgeRegistry()
    k.register_candidate(
        knowledge_id="K1", term="Agent", definition="x",
        definition_type="EXPLICIT_SOURCE", provenance=["SRC-1"], confidence=0.9
    )
    k.canonicalize("K1", approved=True)
    item = k.revoke_support("K1")
    assert item.canonical is False
    assert item.review_status == "REVIEW_REQUIRED"
