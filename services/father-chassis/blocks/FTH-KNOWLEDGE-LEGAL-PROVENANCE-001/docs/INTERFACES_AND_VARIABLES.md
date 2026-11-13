# Interfaces and Variables
Owner: Architect + System Analyst.

SourceUsePolicy:
- policy_id: str
- version: str
- allowed_rights: frozenset[str]
- denied_rights: frozenset[str]
- allowed_access: frozenset[str]
- required_evidence_types: frozenset[str]

PolicyEvidence:
- evidence_id: str
- evidence_type: str
- authority: str
- locator: str
- evidence_hash: str

SourceAdmissibilityDecision:
- decision_id: str
- source_id: str
- status: APPROVED|HOLD|REJECTED
- policy_id: str
- policy_version: str
- allowed_use: tuple[str,...]
- evidence_refs: tuple[str,...]
- reasons: tuple[str,...]

ProvenanceRecord:
- provenance_id: str
- source_id: str
- source_locator: str
- source_version: str
- source_content_hash: str|None
- admissibility_decision_id: str
- evidence_refs: tuple[str,...]
- issuer: str
- created_at: str