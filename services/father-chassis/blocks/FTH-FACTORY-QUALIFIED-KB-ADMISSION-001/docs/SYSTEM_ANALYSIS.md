# System Analysis
Owner: Senior System Analyst.

Requirements:
KB-01 each FactoryAgentContract already declares required KnowledgeBaseContract objects.
KB-02 each required kb_id must resolve to one selected KnowledgeBaseRelease.
KB-03 release has release_id, kb_id, version, release_hash and status.
KB-04 release records source_set_hashes and provenance_refs.
KB-05 release records retrieval_evidence_refs and retrieval_metrics.
KB-06 only status=QUALIFIED is admissible.
KB-07 release kb_id must match required KB.
KB-08 missing release fails closed.
KB-09 hash/provenance/retrieval evidence omissions fail closed.
KB-10 admission decision records every admitted release ID/hash.
KB-11 KB admission is independent from role/competency/tool/security gates.
KB-12 dev/unqualified bypass is not permitted in strict factory mode.

Failure modes:
unknown kb_id, duplicate active releases, unqualified status, empty source set, absent provenance, absent retrieval evidence, malformed hash.