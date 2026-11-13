# Data and State
Owner: System Analyst + Data Architect.

Decision and provenance records are immutable.

Primary identities:
decision_id, provenance_id.

Binding invariant:
ProvenanceRecord.source_id == decision.source_id == intake.source_id.

Hash invariant:
if intake.content_hash exists, provenance.source_content_hash must equal it.

APPROVED requires non-empty evidence_refs and allowed_use.

No raw source bytes are stored in decision/provenance state.