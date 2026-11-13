# Data and State
Owner: System Analyst + Data Architect.

Release identity is immutable:
release_id + kb_id + version + release_hash.

Minimum provenance:
source_set_hashes + provenance_refs.

Minimum retrieval qualification:
retrieval_evidence_refs plus at least one named retrieval metric.

Current registry may be in-memory/reference implementation.
Future Knowledge Factory persists releases in dedicated durable registry.

Workflow stores only decision references:
release_ids, release_hashes, evidence_refs, reasons.

No raw copyrighted source content is stored in admission state.