# FUA-001 Evidence Record — LOCAL EVM TEST 0003A

Evidence ID: EVID-FUA-EVM-0003A
Date: 2026-11-01
Environment: target Windows workstation
Python environment: local .venv
Status: PARTIAL_PASS

## 01. Proven locally

- father-fua editable build: PASS
- father-fua install: PASS
- pytest: 89 passed
- pytest failures: 0
- warning count: 1
- test duration: 1.21 s

Observed warning:
StarletteDeprecationWarning regarding TestClient/httpx transition.
Classification: NON_BLOCKING_TECH_DEBT.

## 02. Runner defect discovered

The original PowerShell health polling used:
1..30 | ForEach-Object { ... break }

On successful health check, break terminated the enclosing script flow before API smoke/full assembly stages.

The runner was corrected to a standard for-loop.

## 03. Still required on target workstation

- live /health confirmation
- POST /v1/assembly/run
- audit chain confirmation
- evidence SHA-256 confirmation
- readiness remains DENIED

## 04. Gate decision

LOCAL_PACKAGE_BUILD: PASS
LOCAL_TEST_SUITE: PASS
LOCAL_FULL_HTTP_ASSEMBLY: NOT_YET_PROVEN
INSTALLATION_PERMIT: DENIED
