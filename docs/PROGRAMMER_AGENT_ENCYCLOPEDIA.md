# Programmer Agent Encyclopedia

**Program:** `FATHER-TRAIN-0001`

## Purpose

This document defines the lab as an encyclopedia of engineering work for the Programmer Agent. The programmer is the central implementation role, but never works in isolation. Every implementation must remain traceable to requirements, architecture, tests, security constraints, review findings, build evidence and lessons learned.

The primary objective is not to collect code snippets. The objective is to accumulate reusable engineering knowledge about how tasks are analyzed, designed, implemented, verified, secured, repaired and improved over time.

## Core interaction model

`SOURCE / TASK`
→ `ANALYST`
→ `ARCHITECT`
→ `SECURITY ENGINEER`
→ `QA / TEST DESIGN`
→ `PROGRAMMER`
→ `CODE REVIEW / CRITIC`
→ `TEST / SECURITY / BUILD`
→ `AUDIT`
→ `LESSONS LEARNED`
→ `REUSABLE PATTERN`
→ `KNOWLEDGE`

The order may iterate. Architecture, security and QA are not one-time gates; they may return findings to the programmer and trigger controlled rework.

## Programmer Agent responsibilities

The Programmer Agent must be able to:

1. Read a requirement without silently expanding or reducing scope.
2. Identify ambiguity and request clarification before coding where needed.
3. Map each implementation unit to one or more requirement IDs.
4. Respect architectural boundaries, interfaces and dependency rules.
5. Respect security constraints before implementation, not after release.
6. Produce code that is testable, observable and reproducible.
7. Explain material engineering decisions and trade-offs.
8. Distinguish reference-derived patterns from its own proposed solution.
9. Respond to review, test and security findings without hiding regressions.
10. Convert repeated successful solutions into reusable patterns.
11. Record failed approaches and anti-patterns so they are not rediscovered repeatedly.
12. Preserve evidence sufficient for another specialist to reproduce the result.

## Architect ↔ Programmer contract

The Architect provides:

- system boundary;
- module decomposition;
- responsibilities and invariants;
- interfaces and contracts;
- dependency direction;
- state and lifecycle model;
- error-handling strategy;
- performance or resource constraints where relevant;
- approved extension points;
- architecture decision records (`ADR`).

The Programmer must return:

- implemented modules mapped to architecture IDs;
- deviations from the proposed architecture;
- newly discovered constraints;
- implementation trade-offs;
- technical debt introduced;
- evidence that the implementation respects interfaces and invariants.

Any material deviation must create an explicit record such as `DEV-ARCH-*`; it must not remain an undocumented implementation accident.

## Security Engineer ↔ Programmer contract

The Security Engineer provides, as applicable:

- trust boundaries;
- asset list and protected data;
- input-validation rules;
- authentication/authorization constraints;
- secrets-handling rules;
- dependency and supply-chain requirements;
- filesystem/network restrictions;
- logging and privacy constraints;
- abuse/misuse cases;
- security acceptance criteria.

The Programmer must demonstrate:

- unsafe inputs fail safely;
- secrets are not embedded in code or fixtures;
- privileged operations are explicit;
- logs do not leak protected information;
- dependencies are declared and reviewable;
- errors do not silently bypass controls;
- security findings are linked to fixes and regression tests where meaningful.

Security is a design input, not a final scan.

## QA ↔ Programmer contract

QA/Test Design provides acceptance criteria and test intentions before implementation where practical.

The Programmer must keep code testable and provide deterministic seams for tests. A defect that escapes a previously defined test intention is recorded separately from a defect caused by a missing test intention. This lets the lab measure both programmer quality and QA quality.

## Knowledge object model

Each meaningful exercise should generate linked objects:

- `SRC-*` — source/book/reference fragment
- `TASK-*` — training task
- `REQ-*` — requirement
- `ADR-*` — architecture decision
- `ARCH-*` — architecture object or boundary
- `SEC-*` — security requirement/finding
- `TEST-*` — test intent/case
- `CODE-*` — implementation unit
- `REV-*` — code review finding
- `DEF-*` — defect
- `FIX-*` — remediation
- `BUILD-*` — reproducibility/build evidence
- `EXP-*` — experiment/A-B comparison
- `PAT-*` — reusable pattern
- `ANTI-*` — anti-pattern
- `LESSON-*` — lesson learned

The graph between these objects is more important than any individual document.

Example:

`REQ-PY-L01-004`
→ `ADR-PY-L01-002`
→ `SEC-PY-L01-001`
→ `TEST-PY-L01-007`
→ `CODE-PY-L01-011`
→ `REV-PY-L01-003`
→ `DEF-PY-L01-002`
→ `FIX-PY-L01-002`
→ `LESSON-PY-L01-005`
→ `PAT-PY-0003`

## Encyclopedia dimensions

The Programmer Encyclopedia will grow along several dimensions.

### Language knowledge

Python → C++ → Go, while keeping the same engineering process where possible.

### Problem knowledge

Input, state, rendering, persistence, networking, concurrency, APIs, databases, authentication, observability, deployment and other implementation domains.

### Architecture knowledge

Layering, modularity, event loops, state machines, ECS-style decomposition where appropriate, ports/adapters, dependency inversion, message passing and other patterns introduced only when justified by the exercise.

### Security knowledge

Validation, trust boundaries, secrets, dependency risk, least privilege, safe persistence, logging, network boundaries and failure handling.

### Failure knowledge

Compilation failures, runtime defects, logic defects, race conditions, test gaps, architecture drift, security findings, performance regressions and release failures.

### Decision knowledge

Why one solution was chosen over another, what evidence supported it, what alternatives were rejected and what later evidence changed the decision.

## Competence measurement

The lab should measure at least:

- requirements implemented correctly;
- requirement loss and unintended scope expansion;
- architecture deviations;
- security findings introduced by implementation;
- review findings per task;
- defects found before and after release gate;
- regression rate;
- build reproducibility;
- time/iterations to first correct implementation;
- repeated mistakes;
- percentage of decisions with provenance;
- reuse of validated patterns;
- ability to transfer a pattern to a different language or domain.

The goal is a competence curve, not a leaderboard.

## Training progression

For each new topic:

1. **Imitation** — repeat a verified reference implementation and understand every step.
2. **Reconstruction** — implement from requirements without seeing the final reference code.
3. **Comparison** — compare our solution with the reference and explain differences.
4. **Variation** — change constraints and adapt the solution.
5. **Transfer** — apply the pattern to another small project or language.
6. **Productionization** — add tests, security, build/release evidence and operational constraints.
7. **Generalization** — extract a reusable pattern or anti-pattern into the encyclopedia.

## Evidence rule

A book, tutorial or reference implementation is evidence of a technique, not evidence that our Programmer Agent can perform it.

Competence is promoted only when the agent produces a reproducible result under controlled requirements and the result survives architecture, QA, security and audit gates.

## First research question

The first Python exercises should answer:

> Can the Programmer Agent reproduce a small book-defined implementation, explain its architecture and security surface, pass independent tests, then solve a similar task with less guidance?

That question is more important than the complexity of the first game.
