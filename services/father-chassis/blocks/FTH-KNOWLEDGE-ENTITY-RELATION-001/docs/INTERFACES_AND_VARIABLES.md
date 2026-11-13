# Interfaces and Variables
Owner: Architect + System Analyst.

ExtractionPolicy:
- policy_id: str
- version: str
- entity_types: tuple[str,...]
- relation_types: tuple[str,...]
- min_confidence: float

EntityRecord:
- entity_id: str
- entity_type: str
- canonical_name: str
- aliases: tuple[str,...]
- confidence: float
- evidence_chunk_ids: tuple[str,...]
- entity_hash: str

RelationRecord:
- relation_id: str
- relation_type: str
- subject_entity_id: str
- object_entity_id: str
- confidence: float
- evidence_chunk_ids: tuple[str,...]
- relation_hash: str

ExtractionSet:
- extraction_set_id: str
- chunk_set_id: str
- chunk_set_hash: str
- extractor_id: str
- extractor_version: str
- policy_id: str
- policy_version: str
- entities: tuple[EntityRecord,...]
- relations: tuple[RelationRecord,...]
- extraction_set_hash: str

ExtractionDecision:
- status: EXTRACTED|REJECTED
- extraction_set: ExtractionSet|None
- diagnostics: tuple[str,...]