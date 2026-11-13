# Interfaces and Variables
Owner: Architect + System Analyst.

KnowledgeBaseRelease:
- release_id: str
- kb_id: str
- version: str
- release_hash: str
- status: str
- source_set_hashes: tuple[str,...]
- provenance_refs: tuple[str,...]
- retrieval_evidence_refs: tuple[str,...]
- retrieval_metrics: dict[str,float]
- created_at: str

KnowledgeAdmissionRequest:
- workflow_id: str
- stage_id: str
- agent_id: str

KnowledgeAdmissionDecision:
- workflow_id: str
- stage_id: str
- agent_id: str
- admitted: bool
- release_ids: tuple[str,...]
- release_hashes: tuple[str,...]
- evidence_refs: tuple[str,...]
- reasons: tuple[str,...]

Registry:
get_for_kb(kb_id) -> KnowledgeBaseRelease | None

Missing/unknown/unqualified/malformed release => BLOCK.