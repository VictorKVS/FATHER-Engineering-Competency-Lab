# Architecture
Owner: Principal/Solution Architect.

FactoryEngineeringWorkflow
        ↓ StageDefinition / owner agent
FactoryAgentCatalog
        ↓ KnowledgeBaseContract[]
QualifiedKnowledgeAdmissionGate
        ├─ KnowledgeReleaseRegistry
        └─ KnowledgeBaseRelease[]
                ↓
release metadata
source-set hashes
provenance refs
retrieval evidence/metrics

Output:
KnowledgeAdmissionDecision -> StageResult knowledge trace.

No prompt/model is allowed to self-declare a KB qualified.