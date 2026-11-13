# Interfaces and Variables
Owner: Architect + System Analyst.

GraphResolutionPolicy:
- policy_id: str
- version: str
- exact_name_same_type_merge: bool

GraphNode:
- node_id: str
- entity_type: str
- canonical_name: str
- source_entity_ids: tuple[str,...]
- evidence_chunk_ids: tuple[str,...]
- node_hash: str

GraphEdge:
- edge_id: str
- relation_type: str
- subject_node_id: str
- object_node_id: str
- source_relation_ids: tuple[str,...]
- evidence_chunk_ids: tuple[str,...]
- edge_hash: str

ResolutionConflict:
- conflict_type: str
- normalized_name: str
- entity_types: tuple[str,...]
- source_entity_ids: tuple[str,...]

KnowledgeGraphSnapshot:
- graph_id: str
- policy_id: str
- policy_version: str
- source_extraction_set_ids: tuple[str,...]
- source_extraction_set_hashes: tuple[str,...]
- nodes: tuple[GraphNode,...]
- edges: tuple[GraphEdge,...]
- conflicts: tuple[ResolutionConflict,...]
- graph_hash: str

GraphBuildDecision:
- status: BUILT|REJECTED
- graph: KnowledgeGraphSnapshot|None
- diagnostics: tuple[str,...]