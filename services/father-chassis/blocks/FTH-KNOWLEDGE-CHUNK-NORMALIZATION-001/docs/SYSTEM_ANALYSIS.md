# System Analysis
Owner: Senior System Analyst.

Requirements:
CN-01 input must be StructuralDocument.
CN-02 normalizer_id/version recorded.
CN-03 chunk_policy_id/version recorded.
CN-04 chunk has chunk_id, ordinal, text, chunk_hash.
CN-05 chunk records source_id/document_id/document_hash.
CN-06 chunk records source_unit_ids and locators.
CN-07 heading context may be prepended deterministically.
CN-08 normalization removes redundant whitespace but preserves textual meaning.
CN-09 chunks non-empty.
CN-10 chunk order deterministic.
CN-11 same document + policy -> same chunk hashes.
CN-12 policy version change explicit in identity.
CN-13 chunks never cross StructuralDocument boundary.
CN-14 oversize paragraphs split deterministically.
CN-15 split lineage points to original unit.
CN-16 no semantic rewriting/summarization in v1.

Reference v1:
max_chars=1200, overlap_chars=0.