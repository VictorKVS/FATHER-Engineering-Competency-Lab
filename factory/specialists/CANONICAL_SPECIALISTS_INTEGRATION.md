# Canonical Specialists Integration

## Purpose

Do not recreate specialists that already exist in the FATHER ecosystem.

The factory must reuse their existing repositories, prompts, processes, tests, knowledge bases and handoff contracts.

## 1. ALINA — analytical / knowledge / process core

Canonical repository:
- VictorKVS/alina-knowledge-worker

Confirmed artifacts:
- AGENTS.md
- README.md
- alina.py
- process_engine.py
- processes/
- docs/knowledge/ALINA_ANALYST_PROCESS_ENGINE_V1.md
- docs/knowledge/process-contract.v1.json
- docs/knowledge/security-audit-result-model.v1.json
- visual/trend analyst protocols
- unit tests

Confirmed process rule:
WORK_RUN
→ WORK_STEP_RUN
→ RESULT / EVIDENCE

A required step only terminates as:
DONE / BLOCKED / NOT_APPLICABLE / REVIEW_REQUIRED.

ALINA role in Factory:
- analyze intent and processes;
- normalize knowledge;
- maintain source/evidence traceability;
- design repeatable specialist processes;
- build and improve specialist knowledge/RAG;
- support training/exams/experience;
- never replace the domain owner for security decisions.

## 2. Information Security Specialist

Existing FATHER role, not to be replaced by ALINA, PM or BA.

Canonical knowledge domains already accumulated in FATHER ecosystem:
- Security KB / Legal Registry
- SecGraph
- regulatory knowledge
- threat/control/risk graph

Ownership:
- applicability;
- information/data classification;
- threats and risks;
- required controls;
- security architecture;
- compliance mapping;
- security acceptance;
- security decision pack.

Security outputs are consumed by Programmer, PIONEER, TIMA, Test Engineer and Polygon.

## 3. PIONEER — AG-005

Canonical repository:
- VictorKVS/CyberED/PIONEER-00

Confirmed role:
Infrastructure Architecture.

Confirmed production chain:
Requirements
→ ALINA traceability review
→ PIONEER logical architecture/topology/specification/threat model/test plan
→ GATE-1
→ TIMA
→ controlled deployment
→ GATE-2

Confirmed artifacts:
- requirements.yaml
- architecture.yaml
- topology.json
- threat-model.md
- bill-of-materials.yaml
- test-plan.yaml
- handoff-to-tima.json
- evidence/

Confirmed restrictions:
- no infrastructure write;
- no cloud credentials;
- no physical network write.

GATE-1 binds architecture/security/source catalog by SHA-256 and must not be interpreted as deployment authorization.

## 4. TIMA / Timofey — AG-003

Existing engineering agent.

Ownership:
- Windows/Linux;
- Docker/Kubernetes;
- Git/CI/CD;
- DevSecOps;
- infrastructure execution;
- isolation/access;
- runtime and AI Security;
- observability/SRE;
- resource control;
- evidence collection.

PIONEER prepares design.
TIMA executes approved infrastructure contract.

TIMA must not silently redesign approved architecture.

Current factory addition:
Lean Container Engineering / Docker Image Diet is part of TIMA DevSecOps knowledge.

## 5. FATHER_CODEX — Programmer

Canonical repository:
- VictorKVS/FATHER_CODEX

Confirmed mission:
Approved Requirements + Architecture
→ maintainable secure tested software
→ provenance and release artifacts.

Confirmed pipeline:
Intake
→ Analyze
→ Design
→ Implement
→ Verify
→ Review
→ Release

FATHER_CODEX is a programmer specialization of the shared FATHER platform, not a competing core.

The new factory Programmer panel is therefore a UI/contract view over FATHER_CODEX, not a new programmer agent.

## 6. Test Engineer

The Test Engineer is a separate professional function.

It consumes:
- requirements;
- algorithms;
- contracts;
- code;
- risks;
- architecture;
- NFR/SLA.

It produces explainable test evidence:
WHY TEST EXISTS
→ source requirement
→ algorithm/contract/risk
→ selected node/edge/chain
→ test procedure
→ oracle
→ PASS/FAIL
→ evidence
→ regression binding.

## Canonical handoff backbone

Customer / Project
→ ALINA
→ domain specialists
→ Security Specialist
→ PIONEER (when infrastructure design is involved)
→ FATHER_CODEX
→ Test Engineer
→ TIMA
→ QA/Evals
→ Optimization
→ RC
→ Polygon
→ Release

This is not a strictly linear sequence for every project. Professional consultations and rework loops are allowed and required.

## Rule for all future specialists

Before creating a new specialist:
1. Search Specialist Registry.
2. Search Agent Zoo.
3. Search existing FATHER repositories.
4. Search existing prompts/RAG/KB/processes.
5. REUSE / WRAP / ADAPT before BUILD.
6. Record provenance to the original specialist assets.
