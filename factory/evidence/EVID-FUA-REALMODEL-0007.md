# FUA-001 Evidence Record — REAL LOCAL MODEL MISSION 0007

Evidence ID: EVID-FUA-REALMODEL-0007
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Discovery and compatibility

Discovered local models: 8
All 8 passed the current local-model compatibility baseline.

## 02. Executed model

Selected model: qwen3-vl:8b-instruct-q4_K_M
Transport: OLLAMA
Endpoint: http://127.0.0.1:11434

Note:
The stage runner selected the first compatible model rather than the runtime's preferred general-text model. This is a selector defect, not a mission failure. It is tracked and corrected after this evidence capture.

## 03. Mission result

MISSION STATUS: PASS
AUDIT OK: true
LATENCY: 7171 ms
RESPONSE LENGTH: 416

Response SHA256:
a64eed601929e512cb5c454152428fd8fc4863565cf1ecbdd4b50222d33dceca

Evidence SHA256:
cbd7cc651d29ed9a83c77dc0ab5a94416c92546395e6338f5187d3f0f092ecf3

## 04. Output quality sanity check

The model returned a coherent short explanation of a universal AI agent chassis.
The response did not claim use of external tools.

## 05. Gate decision

REAL_LOCAL_MODEL_DISCOVERY: PASS
MODEL_COMPATIBILITY_BASELINE: PASS
REAL_LOCAL_MODEL_MISSION: PASS
AUDIT_CHAIN: PASS
RESPONSE_HASH: PASS
EVIDENCE_HASH: PASS

MODEL_SELECTION_POLICY: DEFECT_FOUND_AND_PATCH_REQUIRED
REAL_MODEL_LATENCY_BENCHMARK: NEXT
REAL_MODEL_POLYGON: NEXT

INSTALLATION_PERMIT: DENIED
PRODUCTION_READY: NO
