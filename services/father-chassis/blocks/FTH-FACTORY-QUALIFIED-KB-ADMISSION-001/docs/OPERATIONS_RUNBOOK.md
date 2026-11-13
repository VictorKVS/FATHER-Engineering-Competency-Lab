# Operations Runbook
Owner: DevSecOps/SRE.

Strict factory startup requires a configured QualifiedKnowledgeAdmissionGate and releases for stages that will execute.

Health:
- required kb_ids resolve;
- release status QUALIFIED;
- release hash present;
- provenance and retrieval evidence present.

Incident:
missing/revoked/broken release -> block stage. Do not fall back to model parametric memory.

Upgrade:
new release version must be independently qualified before registry selection changes.

Rollback:
select previous still-qualified immutable release; record release hash in admission evidence.