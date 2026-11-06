# FUA-001 Evidence Record — WINDOWS SANDBOX STRESS EVM 0017

Evidence ID: EVID-FUA-SANDBOX-STRESS-EVM-0017
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Repeated allowlisted execution
ALLOWLIST_PASS=20/20

## 02. Repeated child-process denial
SPAWN_DENIED=20/20

## 03. Repeated timeout termination
TIMEOUT_PASS=5/5

## Gate decision
WINDOWS_SANDBOX_STRESS_EVM=PASS
REPEATED_EXECUTION_STABILITY=PASS
REPEATED_PROCESS_TREE_DENIAL=PASS
REPEATED_TIMEOUT_TERMINATION=PASS

This evidence proves repeatable behavior for the tested Windows Job Object sandbox baseline.
It does not by itself prove AppContainer, hostile native-code containment, or mathematical 100% reliability.

INSTALLATION_PERMIT=DENIED
PRODUCTION_READY=NO
