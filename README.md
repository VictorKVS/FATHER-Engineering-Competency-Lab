# FATHER Engineering Competency Lab

**Program ID:** `FATHER-TRAIN-0001`

A controlled engineering training ground for FATHER specialists. The first curriculum uses game development because it exposes requirements, architecture, implementation, testing, security, CI/CD, UX, review, defects, and feedback in a compact project.

## Training principle

We move **from simple to complex** and do not treat tutorial completion as proof of professional competence.

Each exercise follows the same traceable loop:

`BOOK / REFERENCE → LESSON → REQUIREMENTS → ARCHITECTURE → TEST DESIGN → IMPLEMENTATION → REVIEW → TEST → SECURITY / BUILD → COMPARISON → DEFECTS → LESSONS LEARNED → REUSABLE PATTERN`

The reference book is used as a control source. Where practical, the team first attempts the task independently, then compares the result with the reference implementation.

## Language tracks

The lab is deliberately multi-language:

1. **Python** — first training track; fast feedback, Pygame and small complete projects.
2. **C++** — second track; memory/resource management, performance, build systems, stronger architecture discipline and lower-level game-engine concepts.
3. **Go** — third track; not a traditional AAA game language, but useful for simulation, multiplayer/server backends, networking, tooling and concurrent systems.

The objective is not to prove that one language is "best". The same engineering roles and metrics should survive a change of language.

## Specialist pipeline

- Product / Business Analyst
- System / Software Architect
- QA / Test Designer
- Programmer
- Code Reviewer / Critic
- Security Engineer
- DevSecOps / Build Engineer
- UX / Game Interaction Reviewer
- Auditor / Evidence Reviewer
- Knowledge Engineer

## Evidence IDs

Every important artifact should receive a stable ID, for example:

- `GAME-PY-L01-001`
- `REQ-PY-L01-001`
- `ARCH-PY-L01-001`
- `TEST-PY-L01-001`
- `CODE-PY-L01-001`
- `DEF-PY-L01-001`
- `LESSON-PY-L01-001`

Equivalent prefixes will be used for C++ (`CPP`) and Go (`GO`).

## What we measure

We track requirement loss, architecture rework, defects found by stage, escaped defects, test coverage where meaningful, reproducibility, build failures, security findings, decision provenance, review findings, time-to-fix, repeated mistakes and reusable patterns.

The purpose is to build a measurable competence curve for each specialist and for the team as a whole.

## Current status

`CURRICULUM DESIGN / PRE-EXPERIMENT`

No game is claimed as completed yet. The first objective is to define the Python curriculum and run the first small exercise end-to-end.
