# Competency Weighting and Learning Loop

**Program:** `FATHER-TRAIN-0001`

This document defines how the lab converts lessons, decisions, defects, reviews and evidence into measurable specialist growth.

## Principle

We do not claim that an agent becomes better because it completed a lesson or produced more code. Competence grows only when repeated evidence shows better decisions, fewer repeated defects, stronger transfer to new tasks and better collaboration with adjacent roles.

The first implementation uses **operational weights and coded evidence**, not direct modification of LLM model parameters. Parameter-level fine-tuning may be considered later only after a clean, high-quality training corpus exists.

## Stable evidence objects

Every learning event is attached to stable IDs:

- `REQ-*` requirement
- `ADR-*` architecture decision
- `ARCH-*` architecture artifact
- `SEC-*` security finding/control
- `TEST-*` test artifact
- `CODE-*` implementation artifact
- `REV-*` review finding
- `DEF-*` defect
- `FIX-*` fix
- `BUILD-*` build/release result
- `EXP-*` experiment or A/B comparison
- `PAT-*` reusable pattern
- `ANTI-*` anti-pattern
- `LESSON-*` lesson learned
- `XFER-*` transfer-of-learning proof

## Base competency dimensions

Each specialist is scored on several independent dimensions rather than one opaque score.

1. **Correctness** — does the result satisfy requirements and tests?
2. **Reasoning quality** — are decisions explained and alternatives considered?
3. **Architecture alignment** — does implementation respect boundaries and contracts?
4. **Security alignment** — are trust boundaries, validation, secrets, dependencies and abuse cases handled?
5. **Testability** — can the result be verified deterministically?
6. **Reproducibility** — can another environment reproduce the result?
7. **Maintainability** — is the solution understandable and changeable?
8. **Efficiency** — time/rework/resource cost relative to task complexity.
9. **Defect escape** — which defects were missed until later stages?
10. **Transfer** — can the specialist reuse the learned principle on a different task without copying the reference?

## Initial weights

Weights are configurable by role and task. A default Programmer profile may start with:

- Correctness: 0.20
- Reasoning quality: 0.10
- Architecture alignment: 0.15
- Security alignment: 0.15
- Testability: 0.10
- Reproducibility: 0.10
- Maintainability: 0.10
- Efficiency: 0.05
- Defect escape: 0.03
- Transfer: 0.02

These are **starting weights**, not permanent truth. We update them only after enough experiments show which dimensions predict successful work.

Architect and Security Engineer profiles use different weights. For example, an Architect receives more weight on system boundaries, alternatives, trade-offs and downstream rework; a Security Engineer receives more weight on threat coverage, risk prioritization, negative testing and escaped security findings.

## Event weighting

Not all findings have the same learning value. Each event can receive:

`event_weight = severity × confidence × recurrence × stage_factor × transfer_factor`

Where:

- **severity** — impact of the error or decision;
- **confidence** — quality of evidence supporting the conclusion;
- **recurrence** — repeated mistakes receive increasing penalty;
- **stage_factor** — late discovery is more costly than early discovery;
- **transfer_factor** — success on an unseen but related task is more valuable than exact repetition.

Example: a security defect found by the programmer before review should penalize less than the same defect escaping to release.

## Learning cycle

For every lesson or project:

`TASK → ATTEMPT → REVIEW → EVIDENCE → SCORE → DIAGNOSIS → LESSON → PATTERN/ANTI-PATTERN → RETEST → TRANSFER TASK`

A lesson is not closed until at least one retest occurs. A competence gain is not confirmed until a transfer task demonstrates the skill in a changed context.

## Repeated-error rule

If the same coded anti-pattern repeats, its penalty grows. Example:

- first `ANTI-SEC-INPUT-VALIDATION`: warning + remediation;
- second recurrence: stronger penalty + mandatory focused exercise;
- third recurrence: competence gate blocks promotion until two consecutive clean transfer tasks.

This prevents the system from hiding repeated weaknesses behind high averages elsewhere.

## Positive reinforcement

Successful decisions also accumulate evidence. A candidate `PAT-*` becomes a Golden Pattern only when:

1. it succeeded in more than one task;
2. review found no critical hidden trade-off;
3. architecture and security roles accepted the usage conditions;
4. a transfer task reproduced the benefit;
5. the pattern records when **not** to use it.

## Role-to-role learning

Programmer learning must include feedback from Architect, Security Engineer, QA and Reviewer.

Examples:

- `ARCH-* → CODE-*` measures implementation fidelity;
- `SEC-* → CODE-* → TEST-*` measures security remediation quality;
- `REV-* → FIX-* → XFER-*` measures whether review feedback became durable competence;
- `DEF-*` origin and discovery stage identify which role needs training.

A defect is therefore not automatically assigned to the Programmer. It may originate in requirements, architecture, security analysis, test design or implementation.

## A/B experiments

The lab should periodically compare variants:

- A: task only;
- B: task + book/reference pattern;
- C: task + internal Golden Patterns;
- D: task + specialist collaboration loop.

The same independent evaluation rubric should score all variants. We then measure which context actually improves quality, speed and transfer.

## Competence promotion gates

Promotion from one competence level to another requires a minimum evidence window, for example:

- no critical repeated anti-patterns in the last N tasks;
- target score above threshold across multiple dimensions;
- at least one independent transfer task;
- acceptable defect escape rate;
- architecture/security review passed;
- reproducible build/test evidence.

A single excellent project cannot by itself promote a specialist several levels.

## From operational weights to model training

Three learning layers are intentionally separated:

### Layer 1 — Contextual learning
Use lessons, patterns, anti-patterns, decision records and retrieval to provide better context to agents.

### Layer 2 — Policy/routing adaptation
Adjust prompts, role routing, review depth, required checks and evidence thresholds based on measured performance.

### Layer 3 — Parameter training
Only after we have enough reviewed and licensed data may we create datasets for supervised fine-tuning, preference optimization or other model training. Raw book text, unreviewed generated code and sensitive project material must not be treated as training data by default.

## Minimum dataset record

A future machine-readable learning record should contain at least:

- task ID;
- specialist role/version;
- input requirements;
- relevant source/reference IDs;
- selected decision;
- alternatives;
- implementation/evidence IDs;
- review/security/test results;
- defects and fixes;
- scores by dimension;
- confidence;
- lessons learned;
- reusable pattern/anti-pattern links;
- retest result;
- transfer result.

## Goal

The aim is not to create agents that merely remember more examples. The aim is to create specialists that measurably improve their ability to choose, justify, implement, verify and transfer engineering decisions while working as a coordinated team.
