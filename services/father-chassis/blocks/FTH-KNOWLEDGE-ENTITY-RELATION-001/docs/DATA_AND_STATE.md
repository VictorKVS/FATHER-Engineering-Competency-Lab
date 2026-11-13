# Data and State
Owner: System Analyst + Data Architect.

All records immutable.

Evidence invariant:
every evidence_chunk_id must exist in parent NormalizedChunkSet.

Relation integrity:
subject/object IDs must resolve inside same ExtractionSet.

Hash inputs:
entity_hash = type + canonical_name + aliases + confidence + sorted evidence_chunk_ids.
relation_hash = type + subject + object + confidence + sorted evidence_chunk_ids.
extraction_set_hash = chunk_set identity + extractor/policy identity + ordered entity/relation hashes.

Volatile runtime IDs/timestamps are excluded.