# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR IMPLEMENTATION.

Approved implementation:
- knowledge_factory/entity_graph.py;
- GraphResolutionPolicy;
- GraphNode;
- GraphEdge;
- ResolutionConflict;
- KnowledgeGraphSnapshot;
- GraphBuildDecision;
- DeterministicEntityGraphBuilder;
- exact same-type/name resolution;
- conflict reporting;
- relation endpoint mapping;
- canonical hashes.

Forbidden:
- embedding similarity auto-merge;
- LLM merge authority;
- graph DB persistence;
- inferred relations;
- silent type conflicts.