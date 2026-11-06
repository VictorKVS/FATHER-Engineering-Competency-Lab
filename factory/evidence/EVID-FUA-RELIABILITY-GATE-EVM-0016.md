# FUA-001 Evidence Record — RELIABILITY GATE EVM 0016

Evidence ID: EVID-FUA-RELIABILITY-GATE-EVM-0016
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Deterministic reliability regression suite

Result:
RELIABILITY_TESTS=PASS

Validated areas include:
- audit hash-chain tamper detection;
- evidence full-envelope tamper detection;
- approval four-eyes, replay guard and payload binding;
- bounded recovery and non-retryable security/validation failures;
- non-negative resource accounting;
- context trust and injection filtering;
- compatibility PASS/FAIL/UNKNOWN fail-closed semantics;
- tool deny/failure audit;
- snapshot-bound human acceptance;
- process sandbox regression.

## 02. Windows Job Object active-process limit

Topology:
- Windows venv launcher + base interpreter are treated as the two-process baseline.

Observed:
CHILD_SPAWN=DENIED
ERROR_TYPE=OSError

Decision:
PROCESS_TREE_LIMIT=PASS

## 03. Windows Job Object memory limit

Observed:
MEMORY_LIMIT=PASS
RETURN_CODE=0

Decision:
PROCESS_MEMORY_LIMIT=PASS

## 04. Final evidence audit

Observed:
FINDING_COUNT=0
REPOSITORY_GATE=PASS
FINAL_EVIDENCE_AUDIT=PASS

## 05. Release state

INSTALLATION_PERMIT=DENIED
PRODUCTION_READY=false
NEXT_GATE=HUMAN_ACCEPTANCE

## Gate decision

FUA_001_RELIABILITY_GATE=PASS
TARGET_EVM_RESOURCE_LIMITS=PASS
TARGET_EVM_PROCESS_TREE_LIMIT=PASS
TARGET_EVM_MEMORY_LIMIT=PASS
EVIDENCE_AUDIT=PASS

This does not claim mathematical 100% reliability or final production certification.
