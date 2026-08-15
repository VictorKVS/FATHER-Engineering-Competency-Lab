# FATHER-TRAIN-0001 — Course Operating Model

## Purpose

This repository is organized as a training course, not as a loose collection of code examples. Every lesson must reproduce a professional engineering process from the very beginning: problem framing, analyst specification, architecture, security, test design, implementation, review, build, evidence, lessons learned and reusable knowledge.

The course moves from simple to complex. A simple technical task still receives the same professional treatment as a larger system; only the depth changes.

## Mandatory lesson flow

`SOURCE / BOOK CHAPTER → ANALYST BRIEF → REQUIREMENTS / ACCEPTANCE CRITERIA → ARCHITECTURE → SECURITY REVIEW → TEST DESIGN → IMPLEMENTATION → CODE REVIEW → TEST / BUILD → EVIDENCE → COMPARISON WITH REFERENCE → DEFECTS → LESSONS LEARNED → REUSABLE PATTERN`

No implementation starts before the analyst brief, requirements, architecture notes, security considerations and test intent exist at the level appropriate to the lesson.

## Educational rule

Every lesson must explain not only **what** was done, but also:

- why this problem is being solved now;
- what assumptions were made;
- what constraints exist;
- what alternatives were considered;
- why one alternative was selected;
- what trade-offs were accepted;
- what risks remain;
- what would change at a higher competence level;
- what evidence proves the result;
- what experience should be retained for future tasks.

The course therefore teaches two things simultaneously:

1. how to build the technical result;
2. how a professional engineering team reasons about that result.

## Lesson package

Each lesson is a self-contained educational package:

```text
lessons/<track>/<level>/<lesson-id>/
├── 00_LESSON_PASSPORT.md
├── 01_SOURCE_AND_GOAL.md
├── 02_ANALYST_BRIEF.md
├── 03_REQUIREMENTS.md
├── 04_ARCHITECTURE.md
├── 05_SECURITY_REVIEW.md
├── 06_TEST_DESIGN.md
├── 07_IMPLEMENTATION_NOTES.md
├── 08_REVIEW_FINDINGS.md
├── 09_EVIDENCE.md
├── 10_COMPARISON_WITH_REFERENCE.md
├── 11_DEFECTS_AND_FIXES.md
├── 12_LESSONS_LEARNED.md
└── src/ tests/ assets/
```

For very small exercises, several files may be compact, but the logical stages must not disappear.

## Responsibility chain

### Analyst
Transforms the source material or lesson goal into a clear problem statement, scope, requirements, acceptance criteria and explicit assumptions.

### Architect
Defines structure, boundaries, interfaces, state, data flow and important trade-offs. Architecture must explain why the chosen design is proportionate to the lesson.

### Security Engineer
Reviews trust boundaries, inputs, files, dependencies, secrets, unsafe defaults, failure modes and abuse cases. Security depth scales with the exercise, but the stage is never silently omitted.

### QA / Test Designer
Creates test intent before implementation. Defines what must be proven for the lesson to be considered complete.

### Programmer
Implements against the approved inputs. Any meaningful deviation must be recorded together with the reason.

### Reviewer / Critic
Checks correctness, maintainability, architecture conformance, unnecessary complexity, missed risks and possible simplifications.

### DevSecOps / Build
Checks reproducible execution, dependency setup, build/run instructions and basic automation where appropriate.

### Auditor / Evidence Reviewer
Verifies that claims are supported by evidence and that the lesson is not promoted beyond what was actually demonstrated.

### Knowledge Engineer
Extracts reusable patterns, anti-patterns, decision rules and lessons into the competence knowledge layer.

## Course progression

A lesson is completed only when both the technical result and the engineering explanation are complete. A copied or reproduced reference implementation without decision reasoning does not count as professional competence.

The long-term objective is an encyclopedia of engineering work where each task can be traced from source and requirement to decision, implementation, defect, fix, evidence and reusable experience.
