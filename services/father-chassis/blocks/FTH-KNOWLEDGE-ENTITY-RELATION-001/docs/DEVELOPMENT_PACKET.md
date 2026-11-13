# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR IMPLEMENTATION.

Approved implementation:
- knowledge_factory/entity_relation.py;
- ExtractionPolicy;
- EntityRecord;
- RelationRecord;
- ExtractionSet;
- ExtractionDecision;
- DeterministicRuleExtractor;
- evidence-lineage validation;
- canonical hashes.

Forbidden:
- LLM authoritative extraction in v1;
- cross-document entity resolution;
- graph DB writes;
- inferred facts without observed evidence.