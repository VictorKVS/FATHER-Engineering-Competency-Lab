# Architecture
Owner: Principal/Solution Architect.

K5 ExtractionSet[]
        ↓
GraphResolutionPolicy
        ↓
EntityResolver
        ├─ canonical-key builder
        ├─ merge/conflict engine
        ├─ source->node map
        └─ lineage union
        ↓
GraphBuilder
        ├─ edge endpoint resolver
        ├─ relation deduplicator
        └─ canonical hasher
        ↓
KnowledgeGraphSnapshot
        ↓
K7 Index / Retrieval

Reference v1 remains in-memory and deterministic.
Persistence adapter comes later.