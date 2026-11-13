# Architecture
Owner: Principal/Solution Architect.

K4 NormalizedChunkSet
        ↓
ExtractionPolicy
        ↓
EntityRelationExtractor
        ├─ candidate detector
        ├─ canonicalizer
        ├─ relation detector
        ├─ lineage validator
        └─ canonical hasher
        ↓
ExtractionSet
        ↓
K6 Entity Resolution / Knowledge Graph

Adapter boundary:
extract(chunk_set, policy) -> ExtractionDecision.

Reference adapter:
DeterministicRuleExtractor.