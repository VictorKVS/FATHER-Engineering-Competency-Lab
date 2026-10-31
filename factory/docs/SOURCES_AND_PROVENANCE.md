# FATHER Factory — Sources and Provenance

## Purpose

Every important design decision, requirement, reusable block, security rule, model, agent, tool, book, paper, external repository and implementation pattern must be traceable to its origin.

The goal is simple:

> We must always be able to answer: **where did this come from, what did we take from it, and where is the original source now?**

This prevents the Factory from becoming a collection of undocumented ideas.

---

## Provenance chain

```text
SOURCE
  ↓
SOURCE_ID
  ↓
EXTRACT / IDEA / REQUIREMENT
  ↓
DECISION
  ↓
ARCHITECTURE ELEMENT
  ↓
BLOCK / CHASSIS / POLICY
  ↓
TEST
  ↓
EVIDENCE
  ↓
PRODUCT
```

Every stage should retain the upstream identifiers.

---

## Source classes

### 1. Primary project sources

Examples:

- project conversations;
- FATHER design notes;
- current repository files;
- approved architecture documents;
- specifications written by the project owner.

### 2. External technical sources

Examples:

- official product documentation;
- standards;
- RFCs;
- vendor documentation;
- GitHub repositories;
- framework documentation;
- API specifications.

### 3. Research sources

Examples:

- books;
- academic papers;
- conference talks;
- benchmark reports;
- security research.

### 4. Derived sources

These are artifacts created inside FATHER from other sources:

- architecture decisions;
- normalized requirements;
- block contracts;
- compatibility matrices;
- implementation patterns;
- test plans.

A derived source MUST point back to its upstream sources.

---

## Minimum source record

Each source record should contain:

```text
source_id
type
title
author / owner
origin
location / URL / repository path
version / commit / publication date
retrieved_at
used_for
license
verification_status
upstream_sources
notes
```

Not every field is mandatory in v0.1, but the schema will grow toward this full form.

---

## Stable IDs

Examples:

```text
SRC-BOOK-0001
SRC-PAPER-0001
SRC-GITHUB-0001
SRC-STD-0001
SRC-DOC-0001
SRC-CONV-0001
SRC-FATHER-0001
SRC-ADR-0001
```

An ID never changes after assignment.

If the source moves, update its location, not its ID.

---

## GitHub source rule

For an external GitHub project record:

- repository URL;
- owner;
- repository name;
- branch or tag;
- commit SHA when used for an implementation decision;
- license;
- files or modules inspected;
- what capability was extracted;
- whether code was reused, adapted, or only studied.

Example:

```yaml
source_id: SRC-GITHUB-0017
repository: owner/project
commit: abc123...
license: Apache-2.0
inspected:
  - src/runtime/
  - docs/architecture.md
used_for:
  - multi-agent orchestration comparison
reuse_mode: STUDY_ONLY
```

This is necessary so we can later reconstruct exactly which version influenced FATHER.

---

## Books and papers

For books:

- title;
- author;
- edition;
- year;
- publisher;
- ISBN when available;
- chapter/page range used;
- what was extracted.

For papers:

- title;
- authors;
- publication;
- year;
- DOI/arXiv URL;
- version/date;
- exact section or figure used.

We do **not** write only "idea from a book". We record enough metadata to find the source again.

---

## Decisions

Important architecture decisions should eventually have an ADR:

```text
ADR-0001
Decision: use chassis + reusable blocks
Sources:
  - SRC-FATHER-CONCEPT-001
  - SRC-FATHER-LAB-001
Reason:
  ...
Alternatives:
  ...
Evidence:
  ...
```

This makes the reasoning reconstructable, not just the result.

---

## Evidence principle

Source registration does not prove correctness.

A source can tell us **why we chose something**.

Tests and evidence tell us **whether it actually works**.

Therefore FATHER separates:

```text
PROVENANCE = where knowledge/design came from
EVIDENCE   = proof that the implementation works
```

Both are mandatory for production-ready components.

---

## Required future links

Every production block should ultimately include:

```json
{
  "id": "FTH-BLOCK-...",
  "sources": ["SRC-..."],
  "decisions": ["ADR-..."],
  "tests": ["TEST-..."],
  "evidence": ["EVD-..."]
}
```

This gives us a full chain:

```text
source → decision → block → test → evidence → product
```

That chain is the permanent "where did this come from?" mechanism for FATHER.
