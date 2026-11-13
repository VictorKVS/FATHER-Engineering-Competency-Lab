# Interfaces and Variables
Owner: Architect + System Analyst.

StructuralParseRequest:
- intake: SourceIntakeRecord
- decision: SourceAdmissibilityDecision
- provenance: ProvenanceRecord
- content_bytes: bytes
- media_type: str

StructuralUnit:
- unit_id: str
- ordinal: int
- unit_type: heading|paragraph
- text: str
- locator: str
- source_id: str
- source_content_hash: str

StructuralDocument:
- document_id: str
- source_id: str
- source_content_hash: str
- provenance_id: str
- parser_id: str
- parser_version: str
- units: tuple[StructuralUnit,...]
- document_hash: str

StructuralParseDecision:
- status: PARSED|PARTIAL|REJECTED
- document: StructuralDocument|None
- diagnostics: tuple[str,...]
- evidence_refs: tuple[str,...]