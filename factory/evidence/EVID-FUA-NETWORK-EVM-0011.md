# FUA-001 Evidence Record — WINDOWS NETWORK ISOLATION EVM 0011

Evidence ID: EVID-FUA-NETWORK-EVM-0011
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Firewall state

Administrator: true

Profiles:
- Domain: Enabled
- Private: Enabled
- Public: Enabled

DefaultOutboundAction:
- Domain: NotConfigured
- Private: NotConfigured
- Public: NotConfigured

## 02. Executable identity

Venv Python:
G:\1\FATHER-Engineering-Competency-Lab\.venv\Scripts\python.exe

Base Python:
C:\Users\1\AppData\Local\Programs\Python\Python310\python.exe

## 03. Baseline external connectivity

Target:
api.github.com:443

Result:
CONNECT=PASS

## 04. Temporary OS-enforced outbound block

Rule 1:
FUA-001-SANDBOX-NETWORK-DENY-EVM-VENV
Action=Block
Program=G:\1\FATHER-Engineering-Competency-Lab\.venv\Scripts\python.exe

Rule 2:
FUA-001-SANDBOX-NETWORK-DENY-EVM-BASE
Action=Block
Program=C:\Users\1\AppData\Local\Programs\Python\Python310\python.exe

## 05. Verification

NETWORK_DENY=PASS
ERROR_TYPE=PermissionError

## 06. Cleanup

RULE_CLEANUP=PASS

## 07. Gate decision

NETWORK_ISOLATION_BASELINE: PASS
OS_ENFORCED_EGRESS_DENY: PASS
EXECUTABLE_PATH_COVERAGE: PASS
TEMPORARY_RULE_CLEANUP: PASS

Not yet claimed:
- restricted token / AppContainer;
- filesystem ACL confinement;
- hostile native-code containment.

FINAL_SANDBOX_CERTIFIED: NO
INSTALLATION_PERMIT: DENIED
PRODUCTION_READY: NO
