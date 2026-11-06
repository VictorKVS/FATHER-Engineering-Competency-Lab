# FUA-001 Sandbox Hardening v0.2

Status: IMPLEMENTED / CI VALIDATION REQUIRED

## 20.10 Security invariants

20.10.01 Network denied by default.
20.10.02 Only absolute Windows drive paths may enter the filesystem allowlist.
20.10.03 UNC paths denied.
20.10.04 Windows device paths denied.
20.10.05 Parent traversal cannot escape an allowed root.
20.10.06 Sibling prefix matching is not sufficient for authorization.
20.10.07 Commands are explicit allowlist entries.
20.10.08 Output size is bounded.
20.10.09 Execution timeout remains mandatory.

## 20.11 Threats addressed

- directory traversal
- prefix confusion
- UNC/network-share escape
- device-path bypass
- arbitrary executable launch
- unbounded output exhaustion

## 20.12 Remaining target-EVM proof

This module validates policy decisions only.
Real OS/process/container isolation still requires target workstation testing and cannot be inferred from unit tests.
