# FATHER TRUST & COMPETENCY LAB

> **Project ID:** FATHER-TRUST-COMPETENCY-0001  
> **Status:** FOUNDATION / DESIGN  
> **Parent:** FATHER Engineering Competency Lab  
> **Extraction-ready:** YES

## Purpose

FATHER Trust & Competency Lab is a separable project inside FATHER for four related problems:

1. **Contracts** — machine-readable contracts for components, data, security, qualification and ownership.
2. **Provenance & Ownership Evidence** — verifiable origin, authorship trail, integrity and build/release provenance.
3. **Product Competency** — evidence-based description of what a FATHER product/component can actually do.
4. **Person Competency** — evidence-based description of what an architect/engineer can actually design, build, test and explain.

The project does **not** treat a declaration as proof.

> **No capability is considered proven until evidence exists.**

This is the same engineering principle used by FATHER:

> **No component is considered ready until its operation has been demonstrated in the final system.**

---

## Why this is a separate project

Trust, provenance and competency are useful outside FATHER.

The project therefore follows a hard boundary:

```text
FATHER
  |
  +-- father-chassis
  +-- agents
  +-- domain packs
  +-- knowledge factory
  |
  +-- FATHER TRUST & COMPETENCY LAB
       |
       +-- contracts
       +-- provenance
       +-- evidence
       +-- competency
       +-- qualification
```

FATHER is the first consumer, **not a hard-coded dependency**.

Later this directory can be extracted into a repository such as:

```text
father-trust-competency
```

without changing the conceptual model.

---

## Core model

```text
SUBJECT
   |
   +--> CONTRACTS
   |
   +--> CLAIMS
   |
   +--> EVIDENCE
   |
   +--> QUALIFICATION
   |
   +--> COMPETENCY
   |
   +--> PROVENANCE
   |
   +--> SIGNATURE / HASH / TIMESTAMP
```

A **Subject** may be:

- a person;
- an agent;
- a software block;
- a chassis;
- a product;
- a dataset;
- a model;
- a knowledge source;
- a release.

---

## Five contract classes

### 1. Component Contract
What a block provides, requires and guarantees.

### 2. Data Contract
Schemas, classifications, permitted flows, retention and integrity requirements.

### 3. Security Contract
Trust level, permissions, network/tool boundaries, fail-open/fail-closed behavior and policy obligations.

### 4. Qualification Contract
What tests, gates and evidence are required before a claim may be accepted.

### 5. Ownership / Provenance Contract
Origin repository, authorship evidence, parent artifacts, source commit, hashes, signatures, SBOM/build provenance and release lineage.

---

## Evidence model

```text
CLAIM
  |
  +-- evidence: source
  +-- evidence: commit
  +-- evidence: test
  +-- evidence: qualification
  +-- evidence: artifact hash
  +-- evidence: signed release
  +-- evidence: ADR
  +-- evidence: external certificate
  |
  +--> confidence / level
```

The system distinguishes:

```text
DECLARED     != PROVEN
LEARNED      != DEMONSTRATED
TESTED       != INTEGRATED
INTEGRATED   != QUALIFIED
QUALIFIED    != OWNED
```

---

## Competency model

The same engine evaluates two scopes.

### PERSON competency

Examples:

- AI architecture;
- LLM/RAG;
- AI agents;
- AI security;
- DevSecOps;
- Kubernetes;
- OSINT;
- system design.

Evidence may include:

- completed laboratory work;
- code authored;
- architecture decisions;
- qualified systems;
- reports;
- presentations;
- exams/certifications;
- incident/problem resolution;
- reproducible demonstrations.

### PRODUCT competency

Examples:

- can route between models;
- can survive Redis outage;
- can produce auditable traces;
- can enforce a security contract;
- can execute an agent workflow;
- can retrieve grounded evidence;
- can meet an operational SLO.

Evidence may include:

- automated tests;
- chaos tests;
- security scans;
- load tests;
- endurance tests;
- signed artifacts;
- qualification reports.

The **same claim/evidence/qualification model** is used for people and products.

---

## Competency levels

Initial generic scale:

```text
C0  CLAIMED
C1  LEARNED
C2  DEMONSTRATED
C3  REPEATABLE
C4  INTEGRATED
C5  QUALIFIED
C6  INDUSTRIAL / PROFESSIONAL
```

Domain-specific profiles may refine this scale, but may not weaken evidence requirements.

---

## Trust chain

Target model:

```text
IDEA
 ↓
ADR
 ↓
SIGNED COMMIT
 ↓
SOURCE HASH
 ↓
BUILD PROVENANCE
 ↓
SBOM
 ↓
SIGNED ARTIFACT
 ↓
TEST EVIDENCE
 ↓
QUALIFICATION
 ↓
SIGNED RELEASE
 ↓
TRANSPARENCY / AUDIT LEDGER
```

Technology candidates:

- Git signed commits/tags;
- Sigstore/Cosign;
- SLSA provenance;
- in-toto attestations;
- CycloneDX/SPDX SBOM;
- immutable/append-only evidence log;
- trusted timestamping;
- C2PA where media provenance is relevant.

No technology becomes mandatory until integrated and qualified.

---

## Relationship with FATHER FQDP

FQDP remains the product qualification hierarchy:

```text
L0 BLOCK
L1 SUBSYSTEM
L2 CHASSIS
L3 PRODUCT
L4 FACTORY
L5 PLATFORM FAMILY
```

Trust & Competency Lab provides the **evidence and claim layer** around those levels.

Example:

```text
FATHER CHASSIS
  claim: G6 INDUSTRIAL
        |
        +-- G6.1 evidence
        +-- G6.2 evidence
        +-- G6.3 evidence
        +-- G6.4 evidence
        +-- G6.5 evidence
        +-- G6.6 evidence
        |
        +--> qualification decision
```

---

## Initial modules

```text
contracts/
  component/
  data/
  security/
  qualification/
  ownership/

provenance/
  adr-ledger/
  artifact-lineage/
  build-attestations/
  signatures/

evidence/
  claims/
  artifacts/
  indexes/

competency/
  person/
  product/
  domains/

qualification/
  policies/
  gates/
  reports/

schemas/
docs/
```

Directories are conceptual boundaries first. Implementation is added only when contracts are approved.

---

## Extraction rules

To preserve future standalone use:

1. No imports from `services/father-controller`.
2. FATHER-specific identifiers belong in adapters/profiles, not the core schema.
3. Core schemas must use generic `subject / claim / evidence / contract / qualification` terminology.
4. Repository paths are references, not runtime dependencies.
5. External integrations use adapters.
6. Every FATHER-specific feature must be removable without breaking the core.
7. The project owns its own README, schemas, versioning and migration rules.

---

## First milestones

### TCF-01 — Domain model
Define Subject, Claim, Evidence, Contract, Qualification and Competency.

### TCF-02 — Contract schemas
Machine-readable schemas for five contract classes.

### TCF-03 — Evidence ledger
Hash-linked evidence records with immutable identifiers.

### TCF-04 — Product competency
Import FATHER G6 evidence as the first real product competency case.

### TCF-05 — Person competency
Map architect competencies to verifiable evidence without self-declared inflation.

### TCF-06 — Provenance
Signed commits/tags + artifact hash + SBOM + build attestation.

### TCF-07 — FATHER adapter
Connect FQDP and FATHER block registry without coupling the core.

### TCF-08 — Standalone extraction test
Copy the project outside FATHER and prove its tests/schema validation still work.

---

## Definition of Done for v0.1

v0.1 is ready only when:

- schemas are versioned;
- contracts validate automatically;
- claims can reference evidence;
- product and person competency use the same evidence engine;
- FATHER G6 qualification can be imported as a real example;
- provenance chain can be verified;
- standalone extraction test passes.

---

## Current status

```text
PROJECT BOUNDARY           DEFINED
CONCEPT MODEL              DEFINED
CONTRACT CLASSES           DEFINED
PERSON COMPETENCY MODEL    DEFINED
PRODUCT COMPETENCY MODEL   DEFINED
PROVENANCE TARGET          DEFINED

IMPLEMENTATION             NOT STARTED
QUALIFICATION              NOT STARTED
STANDALONE EXTRACTION      NOT YET PROVEN
```

The project is intentionally not marked ready merely because its architecture exists.
