# Architecture
Owner: Principal/Solution Architect.

K3 StructuralDocument
        ↓
NormalizationPolicy
        ↓
StructuralChunker
        ├─ whitespace normalizer
        ├─ heading-context tracker
        ├─ deterministic size splitter
        ├─ lineage builder
        └─ chunk hasher
        ↓
NormalizedChunkSet
        ↓
K5 Entity/Relation Extraction and/or Indexing

No LLM required in K4 v1.