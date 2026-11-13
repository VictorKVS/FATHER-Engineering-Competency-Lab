# Interfaces and Variables
Owner: Architect + System Analyst.

SourceCandidate:
- source_id: str|None
- source_class: str
- title: str
- locator: str
- version: str|None
- publication_date: str|None
- effective_date: str|None
- content_bytes: bytes|None
- declared_access: str
- declared_rights: str

SourceIntakeRecord:
- source_id: str
- source_class: str
- title: str
- locator: str
- version: str
- publication_date: str|None
- effective_date: str|None
- content_hash: str|None
- hash_algorithm: "sha256"|None
- declared_access: str
- declared_rights: str
- duplicate_of_source_id: str|None
- status: RECEIVED|FINGERPRINTED|INTAKE_READY|REJECTED

SourceIntakeDecision:
- accepted: bool
- record: SourceIntakeRecord|None
- reasons: tuple[str,...]
- evidence_refs: tuple[str,...]