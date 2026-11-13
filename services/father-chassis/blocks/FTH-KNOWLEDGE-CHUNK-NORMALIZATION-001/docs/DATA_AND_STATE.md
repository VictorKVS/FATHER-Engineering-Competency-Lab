# Data and State
Owner: System Analyst + Data Architect.

NormalizedChunkSet immutable.

Lineage invariant:
every chunk source_id/document_id/document_hash equals parent StructuralDocument.

Unit lineage:
every source_unit_id exists in StructuralDocument.units.

Ordering:
chunk ordinals strictly increase from 0.

Hash inputs:
chunk_hash = SHA-256(stable document identity + policy id/version + normalized text + unit lineage).
chunk_set_hash = SHA-256(ordered chunk hashes + normalizer/policy identity).

Volatile runtime IDs/timestamps are not hash inputs.