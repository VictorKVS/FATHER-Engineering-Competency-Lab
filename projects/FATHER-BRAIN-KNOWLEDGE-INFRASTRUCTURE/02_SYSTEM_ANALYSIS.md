# FATHER Brain & Knowledge Infrastructure
## 02 — System Analysis

**Project:** FATHER Brain & Knowledge Infrastructure  
**Stage:** System Analysis  
**Status:** SA DRAFT FOR GATE  
**Input:** 01_BUSINESS_ANALYSIS.md  
**Rule:** no physical architecture or implementation before SA PASS.

---

## 1. System purpose

Provide a platform capability that can design, build, populate, qualify, release, deploy, update, migrate and revoke Brain Packages for agents and products while preserving portability, provenance, evidence and security.

---

## 2. System boundary

The system owns:

- Brain Package lifecycle;
- Knowledge Loading Profile execution;
- canonical knowledge representation;
- storage capability abstraction;
- index generation;
- retrieval profile binding;
- qualification evidence;
- release metadata;
- compatibility metadata;
- migration metadata.

The system integrates with, but does not own:

- Agent runtime;
- UAG;
- POLYGON;
- Product Composer;
- Evidence Ledger;
- Model Zoo;
- Tool/MCP registry;
- deployment platform.

---

## 3. Logical lifecycle

```text
REQUIREMENTS
  ↓
BRAIN SPEC
  ↓
SOURCE ADMISSION
  ↓
INGESTION
  ↓
NORMALIZATION
  ↓
FACT / ENTITY / RELATION PROCESSING
  ↓
CONFLICT / VERSION RESOLUTION
  ↓
CANONICAL KNOWLEDGE SNAPSHOT
  ↓
INDEX BUILD
  ↓
RETRIEVAL PROFILE BINDING
  ↓
QUALIFICATION
  ↓
PACKAGE
  ↓
RELEASE
  ↓
DEPLOY
  ↓
OPERATE / UPDATE
  ↓
MIGRATE / ROLLBACK / REVOKE
```

---

## 4. Core system entities

### BrainSpec
Requested brain class, capabilities, SLO, security class and deployment constraints.

### SourceRecord
Registered knowledge source with trust, rights, classification, version and provenance metadata.

### KnowledgeSnapshot
Immutable logical view of accepted canonical knowledge at a specific version.

### BrainPackage
Portable release artifact referencing a KnowledgeSnapshot, indexes, retrieval policy, security policy and compatibility manifest.

### StorageProfile
Required storage capabilities independent of vendor.

### StorageBinding
Concrete qualified adapter/implementation used for one deployment.

### LoadingProfile
Rules and workflow for acquiring/updating source knowledge.

### RetrievalProfile
Search/retrieval behavior required by the Brain Package.

### QualificationProfile
Tests and thresholds required for a class/use case.

### BrainRelease
Approved immutable version of a Brain Package.

---

## 5. Functional requirements

### FR-01 Brain specification
The system shall create a machine-readable BrainSpec.

### FR-02 Source registration
Every source shall be registered before ingestion.

### FR-03 Source admission
Rejected, unknown or unauthorized sources shall not enter canonical knowledge.

### FR-04 Loading profiles
The system shall support pluggable loading profiles.

### FR-05 Canonical knowledge
Storage implementations shall not become the canonical truth by themselves.

### FR-06 Versioning
Every accepted knowledge state shall be versioned.

### FR-07 Conflict visibility
Conflicting claims shall remain visible until an approved resolver policy produces a resolution state.

### FR-08 Provenance
Every derived knowledge object shall retain lineage to source evidence.

### FR-09 Multi-representation
A KnowledgeSnapshot may generate relational, vector, lexical, graph and object representations.

### FR-10 Storage abstraction
Business logic shall address storage through capability contracts/adapters.

### FR-11 Retrieval abstraction
Retrieval shall be represented as a profile, not hard-coded to one engine.

### FR-12 Packaging
The system shall generate a portable Brain Package manifest.

### FR-13 Qualification
A Brain Package cannot become RELEASED without required qualification evidence.

### FR-14 Compatibility
A release shall declare required agent/runtime/storage/model compatibility constraints.

### FR-15 Migration
The system shall support migration by rebuilding target representations from canonical knowledge where possible.

### FR-16 Rollback
Previously qualified releases shall be selectable for controlled rollback.

### FR-17 Revocation
A compromised or obsolete release shall support explicit revocation.

### FR-18 Audit
All state-changing operations shall be auditable.

---

## 6. Non-functional requirements

### NFR-01 Determinism
Where the selected algorithm is deterministic, repeated processing of identical input and policy versions shall produce identical identity/hash.

### NFR-02 Traceability
Every released artifact shall be traceable to inputs, policies, versions, tests and evidence.

### NFR-03 Portability
A Brain Package shall not require one specific database vendor unless explicitly declared by a product-specific constraint.

### NFR-04 Security
Access shall be fail-closed for protected classes.

### NFR-05 Scalability
The architecture shall support profiles from local embedded deployments to distributed installations.

### NFR-06 Observability
Build, ingest, retrieval, errors, resource use and qualification shall emit metrics/evidence.

### NFR-07 Recoverability
Backup/restore and rollback requirements shall be declared per profile.

### NFR-08 Cost visibility
Resource/cost measurements shall be available for comparison.

### NFR-09 Upgradeability
Schema, index and package formats shall be versioned.

### NFR-10 Testability
Every contract shall have a qualification harness.

---

## 7. State model

### Brain Package lifecycle

```text
DRAFT
  ↓
DESIGNED
  ↓
BUILDING
  ↓
BUILT
  ↓
QUALIFYING
  ├──→ FAILED
  ↓
QUALIFIED
  ↓
RELEASED
  ↓
DEPLOYED
  ├──→ SUPERSEDED
  ├──→ ROLLED_BACK
  └──→ REVOKED
```

Forbidden transitions must be rejected.

---

## 8. Knowledge state model

Each knowledge object must carry at minimum:

- object_id;
- object_type;
- schema_version;
- source lineage;
- source version;
- processing policy version;
- created_at;
- effective_from/effective_to where applicable;
- confidence where applicable;
- classification;
- integrity hash;
- conflict state;
- supersession state.

---

## 9. Storage capability model

The system requires logical capabilities rather than fixed products.

### RelationalStore capability
Required capabilities may include:
- transactional metadata;
- structured querying;
- constraints;
- version records.

### VectorStore capability
Required capabilities may include:
- insert/update/delete;
- vector search;
- metadata filtering;
- configurable similarity;
- index rebuild;
- export/import or rebuild path.

### GraphStore capability
Required capabilities may include:
- nodes;
- edges;
- typed relationships;
- graph traversal;
- integrity constraints;
- graph import/export or rebuild.

### SearchStore capability
Required capabilities may include:
- lexical search;
- filtering;
- ranking;
- facets;
- optional hybrid retrieval.

### ObjectStore capability
Required capabilities may include:
- immutable source/object storage;
- content hashes;
- versioning;
- retention.

### MemoryStore capability
Required capabilities may include:
- low-latency ephemeral state;
- TTL;
- cache invalidation;
- optional streams/queues.

### EvidenceStore capability
Required capabilities:
- append-only or immutability controls;
- hash integrity;
- qualification evidence retrieval;
- release binding.

---

## 10. Storage profile selection inputs

The later decision engine must receive:

- brain_class;
- corpus_size;
- object_count;
- average object size;
- vector count;
- vector dimension;
- graph node/edge count;
- write rate;
- update frequency;
- retrieval mix;
- concurrency;
- latency SLO;
- availability target;
- durability target;
- security class;
- deployment target;
- budget;
- operator skill constraints.

---

## 11. Knowledge Loading Profile contract

Each KLP shall declare:

- accepted source types;
- authentication needs;
- legal/access checks;
- update mode;
- expected frequency;
- checkpoint/resume behavior;
- duplicate policy;
- deletion policy;
- error policy;
- provenance rules;
- security rules;
- output contract;
- qualification tests.

---

## 12. Conflict and version semantics

The system shall distinguish:

- duplicate;
- update;
- contradiction;
- temporal change;
- source disagreement;
- schema change;
- retraction;
- supersession.

Resolution must never silently erase evidence.

A resolved fact shall retain:
- all contributing claims;
- policy used;
- resolution decision;
- timestamp;
- evidence.

---

## 13. Tenancy and isolation

The system shall support at least:

- single-user;
- single-tenant;
- multi-tenant shared infrastructure;
- isolated high-assurance deployment.

Tenant identity shall be part of authorization context.

Cross-tenant retrieval must be prohibited unless explicitly configured.

---

## 14. Security boundaries

Logical trust boundaries:

```text
EXTERNAL SOURCE
   ↓
SOURCE ADMISSION BOUNDARY
   ↓
INGESTION SANDBOX
   ↓
CANONICAL KNOWLEDGE BOUNDARY
   ↓
INDEX / STORAGE BOUNDARY
   ↓
RETRIEVAL AUTHORIZATION
   ↓
UAG / AGENT ACCESS BOUNDARY
   ↓
AGENT
```

Security controls are required at each transition.

---

## 15. Backup / restore requirements

Each storage binding shall declare:

- backup method;
- backup frequency;
- RPO;
- RTO;
- restore test procedure;
- integrity verification;
- dependency order;
- encryption requirement.

A backup is not considered valid until restore is qualified.

---

## 16. Migration requirements

Migration shall preserve:

- canonical identities where semantically applicable;
- provenance;
- version history;
- security classification;
- package/release relation;
- evidence.

Indexes may be rebuilt if they are derivative artifacts.

Canonical knowledge must remain independently recoverable from a specific vendor index.

---

## 17. Retrieval requirements

Retrieval pipeline may combine:

- lexical;
- vector;
- graph;
- structured query;
- filters;
- reranking;
- multi-stage retrieval.

The selected strategy shall be defined in a RetrievalProfile and qualified against a benchmark.

---

## 18. Observability requirements

Required measurements include:

- source ingest success/failure;
- processing throughput;
- rejected records;
- conflict counts;
- index build duration;
- index size;
- retrieval latency p50/p95/p99;
- retrieval quality;
- storage resource use;
- cache hit rate where applicable;
- backup/restore duration;
- migration duration;
- security denials;
- qualification result.

---

## 19. Traceability chain

Required chain:

```text
SourceRecord
 → SourceVersion
 → ProcessingRun
 → CanonicalKnowledgeObject
 → KnowledgeSnapshot
 → IndexBuild
 → BrainPackage
 → QualificationRun
 → BrainRelease
 → Deployment
```

Every arrow must be machine-verifiable.

---

## 20. System acceptance criteria

SA may receive PASS when:

- [x] system boundary defined;
- [x] logical lifecycle defined;
- [x] core entities defined;
- [x] functional requirements defined;
- [x] non-functional requirements defined;
- [x] lifecycle states defined;
- [x] storage capability model defined;
- [x] loading profile contract defined;
- [x] conflict/version semantics defined;
- [x] tenancy/isolation requirements defined;
- [x] backup/restore requirements defined;
- [x] migration requirements defined;
- [x] retrieval requirements defined;
- [x] observability requirements defined;
- [x] traceability chain defined;
- [x] architecture/vendor decisions explicitly deferred.

---

## 21. SA recommendation

Proceed to **Architecture**.

Architect shall now define:

1. Brain Package metamodel;
2. canonical data contracts;
3. storage adapter interfaces;
4. deployment profiles for B1–B6;
5. reference architecture variants;
6. technology evaluation matrix;
7. security/trust architecture;
8. version/migration architecture;
9. integration with existing FATHER services;
10. ADR set;
11. architecture freeze candidate.

No production implementation is authorized before Architecture + Test Architecture gates.
