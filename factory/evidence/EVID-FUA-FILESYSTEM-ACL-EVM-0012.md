# FUA-001 Evidence Record — WINDOWS FILESYSTEM ACL EVM 0012

Evidence ID: EVID-FUA-FILESYSTEM-ACL-EVM-0012
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Baseline workdir write
WORKDIR_WRITE=PASS

## 02. OS-enforced ACL deny
DENY_ACE=PASS
ACCESS=MODIFY_DENY

## 03. Write-denial verification
ACL_DENY=PASS
ERROR_TYPE=PermissionError

## 04. Sentinel integrity
SENTINEL=UNCHANGED

## 05. Cleanup
ACL_CLEANUP=PASS

## 06. Gate decision
FILESYSTEM_ACL_BASELINE=PASS
OS_ENFORCED_WRITE_BOUNDARY=PASS
WORKDIR_WRITE=PASS
PROTECTED_DIR_WRITE_DENY=PASS
SENTINEL_INTEGRITY=PASS
TEMPORARY_ACL_CLEANUP=PASS

Not yet claimed:
- global filesystem confinement;
- restricted token / low-integrity process;
- AppContainer;
- hostile native-code containment;
- VM/container isolation.

FINAL_SANDBOX_CERTIFIED=NO
INSTALLATION_PERMIT=DENIED
PRODUCTION_READY=NO
