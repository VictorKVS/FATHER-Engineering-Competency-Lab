# FUA-001 / 20.Execution Sandbox — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 20.01 Purpose
Constrain code/tool execution by filesystem, network, process, secret and resource boundaries.

## 20.02 Required fields
20.01 Container / VM
20.02 Filesystem Isolation
20.03 Network Isolation
20.04 Process Isolation
20.05 Secret Isolation
20.06 Resource Limits
20.07 Artifact Capture
20.08 Sandbox Evidence

## 20.03 Invariants
- deny network by default;
- resource limits explicit;
- secrets are not inherited implicitly;
- unsafe paths are rejected.

## 20.04 Current decision
BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
