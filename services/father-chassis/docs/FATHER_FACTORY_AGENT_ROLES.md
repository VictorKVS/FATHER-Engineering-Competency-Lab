# FATHER Factory Agents — Role and Knowledge Contracts

## Purpose

FATHER Factory does not use one universal "smart coder" agent.

It uses a controlled engineering team. Each agent has:
- a narrow decision authority;
- explicit inputs and outputs;
- forbidden decisions;
- mandatory checks;
- escalation paths;
- a dedicated knowledge-base contract;
- measurable quality indicators.

Prompts, RAG collections and tools may evolve later without changing these role boundaries.

## Production team

```text
CUSTOMER / BUSINESS OWNER
        ↓
Senior Business Analyst
        ↓
Senior System Analyst
        ↓
Senior Algorithm Engineer
        ↓
Principal / Solution Architect
        ↓
Senior Test Architect
        ↓
APPROVED DEVELOPMENT PACKET
        ↓
Senior Software Engineer
        ↓
Senior DevSecOps / SRE
        ↓
Qualification / Evidence Auditor
        ↓
HUMAN APPROVAL where required
        ↓
QUALIFIED PRODUCT
```

## 1. Senior Business Analyst

### Owns
- business goal;
- stakeholders;
- business process;
- business value;
- KPIs;
- process optimization;
- business constraints.

### Must not decide
- code;
- API schemas;
- software architecture.

### Knowledge base: KB-BUSINESS-ANALYSIS

Fill with:
- company strategy and objectives;
- process regulations and SOPs;
- stakeholder interviews;
- KPI trees and scorecards;
- service/product catalog;
- business rules;
- cost/revenue models;
- process-mining evidence;
- accepted business-analysis methods and examples.

Core graph:
`goal → process → step → actor → input/output → KPI → value`.

## 2. Senior System Analyst

### Owns
- system requirements;
- use cases;
- states/events;
- data semantics;
- interface semantics;
- failure modes;
- traceability to business goals.

### Must not decide
- final algorithm;
- code-level implementation.

### Knowledge base: KB-SYSTEM-ANALYSIS

Fill with:
- approved BusinessProcessSpec;
- requirements engineering standards;
- use-case/state-machine patterns;
- enterprise data dictionary;
- current APIs and message schemas;
- NFR catalogs;
- historical incidents and failure modes;
- system constraints and dependencies.

Core graph:
`business requirement → system requirement → state/event → data → interface → failure`.

## 3. Senior Algorithm Engineer

### Owns
- feasible solution alternatives;
- algorithm comparison;
- complexity;
- benchmarks;
- quality/cost/latency trade-offs;
- selected AlgorithmSpec.

### Must not decide
- business goal;
- undocumented system semantics;
- final code structure.

### Knowledge base: KB-ALGORITHMS

Fill with:
- algorithms and data structures;
- research papers;
- benchmark reports;
- internal experiment results;
- latency/quality/cost tables;
- failure patterns;
- scaling laws;
- model/RAG/search/routing strategies;
- project constraints and target hardware.

Core graph:
`problem → candidate algorithm → benchmark → metric → constraint → selected variant`.

## 4. Principal / Solution Architect

### Owns
- blocks;
- boundaries;
- interfaces;
- variables and their owners;
- states;
- constants;
- dependencies;
- quality attributes;
- security boundaries;
- architecture patterns.

### Must not
silently change business intent or approved algorithm.

### Knowledge base: KB-ARCHITECTURE

Fill with:
- FATHER Chassis contracts;
- approved ADRs;
- reference architectures;
- distributed-system patterns;
- AI/RAG/agent architecture patterns;
- API/event/data-contract patterns;
- security architecture;
- sizing/capacity guidance;
- anti-patterns and past architecture failures.

Core graph:
`requirement → algorithm → block → interface → variable → state → dependency → quality attribute`.

## 5. Senior Test Architect / QA

### Owns
- acceptance criteria;
- block-output expectations;
- negative/boundary tests;
- correctness/completeness;
- latency;
- resource limits;
- recovery expectations;
- evidence requirements.

Tests are derived before implementation.

### Knowledge base: KB-TEST-ENGINEERING

Fill with:
- requirements and ArchitectureSpec;
- testing strategies;
- contract-testing patterns;
- property-based testing;
- security testing;
- load/performance models;
- chaos/recovery patterns;
- SLO/SLA examples;
- defect/incident history.

Core graph:
`requirement → criterion → metric → threshold → test → evidence`.

## 6. Senior Software Engineer

### Owns only implementation choice

May choose:
- language constructs;
- internal mini-blocks;
- appropriate libraries;
- data structures;
- refactoring;
- cache/async implementation;
- performance optimizations;
- implementation patterns.

Must NOT invent or change:
- variable semantics;
- API fields;
- state ownership;
- approved algorithm;
- security contract;
- acceptance threshold.

### Knowledge base: KB-SOFTWARE-ENGINEERING

Fill with:
- official language documentation;
- approved library documentation;
- coding standards;
- internal reusable components;
- design patterns;
- performance guidance;
- secure coding rules;
- known defects/CVEs relevant to dependencies;
- successful internal implementations.

Core graph:
`contract → implementation option → component/library → quality attribute → code evidence`.

## 7. Senior DevSecOps / SRE

### Owns
- reproducible builds;
- CI/CD;
- deployment;
- runtime resource controls;
- SBOM;
- security scans;
- observability;
- rollback/recovery;
- production evidence.

### Knowledge base: KB-DEVSECOPS

Fill with:
- Git/GitHub standards;
- Docker/OCI;
- Kubernetes;
- IaC;
- CI/CD patterns;
- supply-chain security;
- SLSA/in-toto/Sigstore as they are adopted;
- SBOM standards;
- observability/SRE;
- runbooks;
- incident/recovery history.

Core graph:
`source → build → artifact → SBOM/signature → deployment → runtime → metrics → rollback`.

## 8. Qualification / Evidence Auditor

Independent from implementers.

### Owns
- evidence acceptance;
- criterion-by-criterion qualification;
- provenance verification;
- blocking findings;
- final machine-readable qualification recommendation.

### Must never
- invent evidence;
- silently waive a blocking requirement;
- modify a product merely to make it pass.

### Knowledge base: KB-QUALIFICATION-EVIDENCE

Fill with:
- FQDP rules;
- test contracts;
- qualification policies;
- evidence schemas;
- provenance rules;
- hashes/signatures;
- test/security/runtime evidence;
- competency policies;
- previous qualification failures and lessons learned.

Core graph:
`subject → claim → criterion → evidence → provenance → qualification decision`.

## Knowledge Factory requirements

Every agent KB must be populated through the same controlled lifecycle:

```text
SOURCE
  ↓
LEGAL / ACCESS CHECK
  ↓
FINGERPRINT / HASH
  ↓
METADATA + VERSION
  ↓
PARSE
  ↓
CHUNK
  ↓
ENTITY / RELATION EXTRACTION
  ↓
NORMALIZATION
  ↓
GRAPH
  ↓
QUALITY / CONFLICT CHECK
  ↓
INDEX
  ↓
RETRIEVAL TEST
  ↓
QUALIFIED KB RELEASE
```

Required metadata for every knowledge source:
- source_id;
- title;
- author/owner;
- source class;
- version;
- effective/publication date;
- locator/page/section;
- content hash;
- provenance;
- legal/access status;
- domain;
- supersedes/superseded_by where applicable.

## Prompt layering

Prompts come later and must not replace contracts.

Recommended structure:

```text
ROLE CONTRACT
+ AUTHORITY BOUNDARY
+ CURRENT DEVELOPMENT PACKET
+ DOMAIN POLICIES
+ RETRIEVED KNOWLEDGE
+ TOOL CONTRACTS
+ TASK
+ OUTPUT SCHEMA
```

The model prompt may change. The role contract remains stable and versioned.

## Future competency model

Each factory agent will later receive:
- competency profile;
- required C-level per task;
- training curriculum;
- benchmark suite;
- RAG collection;
- tool permissions;
- historical performance;
- qualification evidence.

An agent is not promoted because its prompt sounds better. It is promoted only after evidence.
