# FUA-001 Evidence Record — WINDOWS RESTRICTED TRUSTLEVEL EVM 0013

Evidence ID: EVID-FUA-RESTRICTED-TRUSTLEVEL-EVM-0013
Date: 2026-11-01
Environment: target Windows workstation
Status: BLOCKED_BY_OS_CAPABILITY

## 01. Probe
Command:
runas /showtrustlevels

Result:
Basic User trust level 0x20000 was not available on the target workstation.

## 02. Gate decision
RESTRICTED_TRUSTLEVEL_BASELINE=BLOCKED_BY_OS_CAPABILITY

This is not counted as PASS and not counted as implementation failure.

Already proven sandbox controls:
- process execution baseline;
- environment scrubbing;
- executable allowlist;
- timeout termination;
- outbound network isolation;
- filesystem ACL write boundary.

Still not proven:
- restricted token / low integrity;
- AppContainer;
- hostile native-code containment;
- VM/container isolation.

INSTALLATION_PERMIT=DENIED
PRODUCTION_READY=NO
