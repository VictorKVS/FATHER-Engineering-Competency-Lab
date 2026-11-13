# System Analysis
Owner: Senior System Analyst.

Requirements:
ER-01 input must be NormalizedChunkSet.
ER-02 extractor_id/version recorded.
ER-03 extraction policy id/version recorded.
ER-04 EntityRecord includes entity_id, entity_type, canonical_name, aliases, confidence.
ER-05 RelationRecord includes relation_id, relation_type, subject_entity_id, object_entity_id, confidence.
ER-06 entity/relation evidence_chunk_ids required.
ER-07 every evidence chunk must exist in input chunk set.
ER-08 every relation subject/object must exist in emitted entity set.
ER-09 same input + extractor/policy -> same extraction hashes.
ER-10 no hidden inference in reference v1.
ER-11 duplicate entity mentions within one chunk may normalize to one entity.
ER-12 extractor diagnostics explicit.
ER-13 unknown/unsupported pattern yields no fact, not hallucinated fact.
ER-14 extraction_set_hash deterministic.

Reference v1:
rule-based capitalized-term entity extraction plus explicit 'X -> Y' relation syntax for testability only.