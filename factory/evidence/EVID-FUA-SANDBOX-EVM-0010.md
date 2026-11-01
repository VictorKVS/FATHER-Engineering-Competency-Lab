# FUA-001 Evidence Record — WINDOWS PROCESS SANDBOX EVM 0010

Evidence ID: EVID-FUA-SANDBOX-EVM-0010
Date: 2026-11-01
Environment: target Windows workstation
Status: PASS

## 01. Allowlisted process execution

RETURN_CODE: 0
TIMED_OUT: false
STDOUT:
SANDBOX=1
CWD=C:\Users\1\AppData\Local\Temp\fua-sandbox-0vnewu_a

## 02. Environment isolation

Parent variable:
FUA_PARENT_SECRET=SHOULD_NOT_LEAK

Child result:
SECRET_VISIBLE=MISSING

Decision:
ENVIRONMENT_SCRUBBING=PASS

## 03. Executable allowlist

Attempted executable:
cmd.exe

Result:
CMD_DENY=PASS

Decision:
EXECUTABLE_ALLOWLIST=PASS

## 04. Timeout and termination

Long-running child process:
sleep 30 seconds

Sandbox timeout:
0.5 seconds

Result:
TIMED_OUT=true

Decision:
TIMEOUT_TERMINATION=PASS

## 05. Gate decision

PROCESS_ISOLATION_BASELINE: PASS
ALLOWLIST_EXECUTION: PASS
ENVIRONMENT_ISOLATION: PASS
SHELL_DENY: PASS
TIMEOUT_TERMINATION: PASS
TEMP_WORKDIR_ISOLATION: PASS

Not yet claimed:
- OS-enforced network isolation;
- restricted token / AppContainer;
- filesystem ACL confinement;
- VM/container boundary;
- hostile native-code containment.

Therefore:
REAL_SANDBOX_PROCESS_BASELINE=PASS
FINAL_SANDBOX_CERTIFIED=NO
INSTALLATION_PERMIT=DENIED
PRODUCTION_READY=NO
