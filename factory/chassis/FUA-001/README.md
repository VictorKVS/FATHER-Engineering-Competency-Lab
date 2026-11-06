# FUA-001 — Canonical Engineering Package Index

Version: 0.2
Status: FULL ASSEMBLY IMPLEMENTED / INSTALLATION NOT APPROVED

## 00. Master specification
- `factory/specs/FUA-001-MASTER-SPEC-v0.2.md`

## 01. Architecture
- `factory/chassis/FUA-001/FUA-001-C4.md`
- `factory/chassis/FUA-001/FUA-001-ASSEMBLY-RUNTIME.md`
- `factory/chassis/FUA-001/FUA-001-FULL-ASSEMBLY-v0.2.md`

## 02. API
- `factory/api/fua-001-openapi.yaml`
- `factory/api/FUA-001-API-DESIGN.md`
- live integration endpoint: `POST /v1/assembly/run`

## 03. Block designs
01. Identity
02. Role
03. Goal
04. Task Planner
05. State
06. Memory
07. Prompt Runtime
08. RAG Runtime
09. Knowledge Runtime
10. Tool Runtime
11. Model Router
12. Policy Engine
13. Evaluator
14. Audit
15. Observability
16. Skill Runtime
17. Context Manager
18. Reflection / Learning
19. Human Approval
20. Execution Sandbox
21. Cost / Resource Controller
22. Evidence Manager
23. Compatibility Manager
24. Failure Recovery
25. Release / Readiness Gate
26. Security Operating Layer

## 04. Executable runtime
- `father_fua/` contains prototype executable representatives for blocks 01-26.
- `tests/` contains component, API and assembly tests.
- `scripts/test-fua-local.ps1` performs the local workstation package/test/API/full-assembly smoke line.

## 05. Standards
- `factory/standards/FATHER-TEST-BLOCK-STANDARD-v0.1.md`

## 06. Evidence
- `factory/evidence/EVID-FUA-LOCAL-0001.md`
- GitHub Actions FUA-001 API workflow validates component/API/assembly behavior.

## 07. Current proof status

- component runtime: CI PASS
- first assembly runtime: CI PASS
- full 01-26 assembly runtime: CI PASS
- full assembly HTTP endpoint: CI PASS
- local full 01-26 HTTP assembly: awaiting next workstation run
- installation permit: DENIED
- production ready: NO

## 08. Next automated factory gates

STATIC VALIDATION
→ SAST
→ SCA
→ SBOM
→ SECRET SCAN
→ API NEGATIVE/FUZZ TESTS
→ COMPATIBILITY HARDENING
→ RED TEAM
→ POLYGON
→ EVIDENCE AUDIT
→ LOCAL EVM FULL ASSEMBLY

## 09. Release rule

No green unit/CI/assembly test alone means PRODUCTION_READY.
FATHER requires all mandatory gates and evidence.
