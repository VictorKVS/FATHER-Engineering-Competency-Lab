from dataclasses import replace

from father.knowledge_factory.chunk_normalization import (
    ChunkPolicy,
    DeterministicStructuralChunker,
)
from father.knowledge_factory.structural_parser import (
    StructuralDocument,
    StructuralUnit,
)


def _document():
    units = (
        StructuralUnit(
            "UNIT-000000", 0, "heading", "# TITLE", "line:1-1", "SRC-1", "a" * 64
        ),
        StructuralUnit(
            "UNIT-000001",
            1,
            "paragraph",
            "First    paragraph   with   extra whitespace.",
            "line:3-3",
            "SRC-1",
            "a" * 64,
        ),
        StructuralUnit(
            "UNIT-000002",
            2,
            "paragraph",
            "Second paragraph.",
            "line:5-5",
            "SRC-1",
            "a" * 64,
        ),
    )
    return StructuralDocument(
        document_id="DOC-1",
        source_id="SRC-1",
        source_content_hash="a" * 64,
        provenance_id="PRV-1",
        parser_id="PARSER",
        parser_version="1.0",
        units=units,
        document_hash="b" * 64,
    )


def test_valid_document_chunks_with_deterministic_hashes():
    chunker = DeterministicStructuralChunker()
    policy = ChunkPolicy("POL-1", "1.0", max_chars=120)
    first = chunker.chunk(_document(), policy)
    second = chunker.chunk(_document(), policy)

    assert first.status == "CHUNKED"
    assert second.status == "CHUNKED"
    assert first.chunk_set.chunk_set_hash == second.chunk_set.chunk_set_hash
    assert [c.chunk_hash for c in first.chunk_set.chunks] == [
        c.chunk_hash for c in second.chunk_set.chunks
    ]


def test_whitespace_is_normalized_without_rewrite():
    result = DeterministicStructuralChunker().chunk(
        _document(), ChunkPolicy("POL-1", "1.0", max_chars=120)
    )
    text = " ".join(chunk.text for chunk in result.chunk_set.chunks)
    assert "First paragraph with extra whitespace." in text
    assert "Second paragraph." in text


def test_lineage_and_locators_are_preserved():
    result = DeterministicStructuralChunker().chunk(
        _document(), ChunkPolicy("POL-1", "1.0", max_chars=120)
    )
    chunk = result.chunk_set.chunks[0]
    assert chunk.source_id == "SRC-1"
    assert chunk.document_id == "DOC-1"
    assert "UNIT-000001" in chunk.source_unit_ids
    assert "line:3-3" in chunk.source_locators


def test_no_empty_chunks_are_created():
    result = DeterministicStructuralChunker().chunk(
        _document(), ChunkPolicy("POL-1", "1.0", max_chars=30)
    )
    assert all(chunk.text.strip() for chunk in result.chunk_set.chunks)


def test_oversize_paragraph_splits_deterministically():
    long_text = "word " * 50
    document = replace(
        _document(),
        units=(
            _document().units[0],
            replace(_document().units[1], text=long_text),
        ),
    )
    policy = ChunkPolicy("POL-1", "1.0", max_chars=40)
    first = DeterministicStructuralChunker().chunk(document, policy)
    second = DeterministicStructuralChunker().chunk(document, policy)
    assert first.status == "CHUNKED"
    assert len(first.chunk_set.chunks) > 1
    assert [c.text for c in first.chunk_set.chunks] == [
        c.text for c in second.chunk_set.chunks
    ]
    assert all(len(c.text) <= policy.max_chars for c in first.chunk_set.chunks)


def test_policy_version_changes_identity_explicitly():
    chunker = DeterministicStructuralChunker()
    first = chunker.chunk(_document(), ChunkPolicy("POL-1", "1.0", max_chars=120))
    second = chunker.chunk(_document(), ChunkPolicy("POL-1", "2.0", max_chars=120))
    assert first.chunk_set.chunk_set_hash != second.chunk_set.chunk_set_hash


def test_cross_document_lineage_mismatch_is_rejected():
    bad_unit = replace(_document().units[1], source_id="OTHER")
    bad = replace(_document(), units=(_document().units[0], bad_unit))
    result = DeterministicStructuralChunker().chunk(
        bad, ChunkPolicy("POL-1", "1.0")
    )
    assert result.status == "REJECTED"
    assert any("source_id mismatch" in x for x in result.diagnostics)


def test_overlap_is_rejected_in_v1():
    result = DeterministicStructuralChunker().chunk(
        _document(), ChunkPolicy("POL-1", "1.0", overlap_chars=10)
    )
    assert result.status == "REJECTED"
    assert "overlap_chars must be 0 in v1" in result.diagnostics
