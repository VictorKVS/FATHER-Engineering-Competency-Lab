# System Analysis
Owner: Senior System Analyst.

Requirements:
GR-01 input extraction sets must have unique IDs/hashes.
GR-02 graph policy id/version recorded.
GR-03 GraphNode has node_id, entity_type, canonical_name, source_entity_ids, evidence_chunk_ids.
GR-04 GraphEdge has edge_id, relation_type, subject_node_id, object_node_id, source_relation_ids, evidence_chunk_ids.
GR-05 node merge only when policy explicitly permits.
GR-06 v1 auto-merge only exact normalized canonical_name + same entity_type.
GR-07 same normalized name with different type -> conflict, no merge.
GR-08 relation endpoints must resolve to nodes.
GR-09 evidence lineage union deterministic.
GR-10 graph node/edge hashes deterministic.
GR-11 graph_snapshot_hash deterministic.
GR-12 input order must not change graph identity.
GR-13 unknown/dangling relation -> REJECTED.
GR-14 conflicts are reported explicitly.
GR-15 no new inferred edge types in v1.