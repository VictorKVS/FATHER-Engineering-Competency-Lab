# FUA-001 Evidence Record — LOCAL EVM FULL ASSEMBLY 0003

Evidence ID: EVID-FUA-EVM-0003
Date: 2026-11-01
Environment: target Windows workstation
Repository: G:\1\FATHER-Engineering-Competency-Lab
Branch: factory-v0.1
Status: PASS

## 01. Local package and test suite

- father-fua editable build: PASS
- father-fua install: PASS
- pytest: 89 passed
- pytest failures: 0
- warning count: 1
- test duration: 1.21 s

Non-blocking warning:
StarletteDeprecationWarning regarding TestClient/httpx transition.

## 02. Live HTTP / full assembly smoke

Runner:
scripts/test-fua-smoke.ps1

Observed result:
- HEALTH: PASS
- ASSEMBLY STATUS: PASS
- AUDIT OK: True
- READINESS: DENIED
- LOCAL HTTP / FULL ASSEMBLY RESULT: PASS

Evidence SHA-256:
70817f8ba002ff9c69cd29e4d48eaa02fa65fc690b752d50e69278ba4324f24a

## 03. Proven on target workstation

- live FastAPI startup;
- /health reachable;
- POST /v1/assembly/run executable;
- full prototype chain 01-26 completes;
- audit hash-chain verifies;
- evidence hash emitted;
- readiness correctly remains DENIED.

## 04. Gate decision

LOCAL_PACKAGE_BUILD: PASS
LOCAL_TEST_SUITE: PASS
LOCAL_LIVE_HTTP: PASS
LOCAL_FULL_01_26_ASSEMBLY: PASS
LOCAL_AUDIT_CHAIN: PASS
LOCAL_EVIDENCE_HASH: PASS

INSTALLATION_PERMIT: DENIED
PRODUCTION_READY: NO

## 05. Next factory gates

- real local model discovery;
- real local model adapter;
- model capability/health test;
- prompt/model compatibility;
- local model mission execution;
- real sandbox isolation;
- compatibility hardening;
- red-team campaign;
- full POLYGON;
- evidence audit;
- human acceptance.
