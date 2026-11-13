# Interfaces and Variables
Owner: Architect + System Analyst.

StageCompetencyPolicy:
- stage_id: str
- domain: str
- capability: str
- minimum_level: str (C0..C6)
- minimum_evidence_count: int >= 0
- required_evidence_types: frozenset[str]

CompetencyAdmissionRequest:
- workflow_id: str
- stage_id: str
- agent_id: str

CompetencyAdmissionDecision:
- workflow_id: str
- stage_id: str
- agent_id: str
- admitted: bool
- trust_qualification_id: str|null
- requested_level: str
- evidence_ids: tuple[str,...]
- reasons: tuple[str,...]

Trust adapter:
get_claim(agent_id, domain, capability) -> Claim|null
get_evidence(agent_id, claim_id) -> tuple[EvidenceRecord,...]
qualify(claim,evidence,policy) -> Trust QualificationDecision

Unknown stage/agent/claim/adapter failure -> fail closed.