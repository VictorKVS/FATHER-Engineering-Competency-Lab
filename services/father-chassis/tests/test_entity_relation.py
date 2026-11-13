from dataclasses import replace

from father.knowledge_factory.chunk_normalization import (
    NormalizedChunk,
    NormalizedChunkSet,
)
from father.knowledge_factory.entity_relation import (
    DeterministicRuleExtractor,
    ExtractionPolicy,
)


def _chunk_set(text="Alpha -> Beta. Alpha works with Gamma."):
    chunk = NormalizedChunk(
        chunk_id="CHK-1",
        ordinal=0,
        text=text,
        chunk_hash="a" * 64,
        source_id="SRC-1",
        document_id="DOC-1",
        document_hash="b" * 64,
        source_unit_ids=("UNIT-1",),
        source_locators=("line:1-1",),
        policy_id="POL-C",
        policy_version="1.0",
    )
    return NormalizedChunkSet(
        chunk_set_id="CHSET-1",
        source_id="SRC-1",
        document_id="DOC-1",
        document_hash="b" * 64,
        normalizer_id="NORM",
        normalizer_version="1.0",
        policy_id="POL-C",
        policy_version="1.0",
        chunks=(chunk,),
        chunk_set_hash="c" * 64,
    )


def test_valid_chunk_set_extracts_entities_and_relation():
    result = DeterministicRuleExtractor().extract(
        _chunk_set(),
        ExtractionPolicy("POL-E", "1.0"),
    )
    assert result.status == "EXTRACTED"
    names = {entity.canonical_name for entity in result.extraction_set.entities}
    assert {"Alpha", "Beta", "Gamma"} <= names
    assert len(result.extraction_set.relations) == 1


def test_same_input_policy_is_deterministic():
    extractor = DeterministicRuleExtractor()
    policy = ExtractionPolicy("POL-E", "1.0")
    first = extractor.extract(_chunk_set(), policy)
    second = extractor.extract(_chunk_set(), policy)
    assert first.extraction_set.extraction_set_hash == second.extraction_set.extraction_set_hash
    assert [e.entity_hash for e in first.extraction_set.entities] == [
        e.entity_hash for e in second.extraction_set.entities
    ]


def test_every_fact_has_chunk_evidence():
    result = DeterministicRuleExtractor().extract(
        _chunk_set(),
        ExtractionPolicy("POL-E", "1.0"),
    )
    assert all(entity.evidence_chunk_ids for entity in result.extraction_set.entities)
    assert all(relation.evidence_chunk_ids for relation in result.extraction_set.relations)


def test_duplicate_mentions_deduplicate_entities():
    result = DeterministicRuleExtractor().extract(
        _chunk_set("Alpha Alpha Alpha -> Beta"),
        ExtractionPolicy("POL-E", "1.0"),
    )
    alpha = [
        entity for entity in result.extraction_set.entities
        if entity.canonical_name == "Alpha"
    ]
    assert len(alpha) == 1


def test_unsupported_text_does_not_invent_relations():
    result = DeterministicRuleExtractor().extract(
        _chunk_set("Alpha and Beta appear in this sentence."),
        ExtractionPolicy("POL-E", "1.0"),
    )
    assert result.status == "EXTRACTED"
    assert result.extraction_set.relations == ()


def test_policy_version_changes_identity():
    extractor = DeterministicRuleExtractor()
    first = extractor.extract(_chunk_set(), ExtractionPolicy("POL-E", "1.0"))
    second = extractor.extract(_chunk_set(), ExtractionPolicy("POL-E", "2.0"))
    assert first.extraction_set.extraction_set_hash != second.extraction_set.extraction_set_hash


def test_malformed_chunk_lineage_is_rejected():
    bad_chunk = replace(_chunk_set().chunks[0], source_id="OTHER")
    bad_set = replace(_chunk_set(), chunks=(bad_chunk,))
    result = DeterministicRuleExtractor().extract(
        bad_set,
        ExtractionPolicy("POL-E", "1.0"),
    )
    assert result.status == "REJECTED"
    assert any("source_id mismatch" in item for item in result.diagnostics)


def test_confidence_is_bounded():
    result = DeterministicRuleExtractor().extract(
        _chunk_set(),
        ExtractionPolicy("POL-E", "1.0", min_confidence=0.8),
    )
    for entity in result.extraction_set.entities:
        assert 0.0 <= entity.confidence <= 1.0
    for relation in result.extraction_set.relations:
        assert 0.0 <= relation.confidence <= 1.0


def test_invalid_policy_is_rejected():
    result = DeterministicRuleExtractor().extract(
        _chunk_set(),
        ExtractionPolicy("POL-E", "1.0", min_confidence=1.5),
    )
    assert result.status == "REJECTED"
    assert "min_confidence must be within [0,1]" in result.diagnostics
