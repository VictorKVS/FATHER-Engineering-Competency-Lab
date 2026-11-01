# FUA-001 Windows Network Isolation EVM v0.1

Purpose:
prove an OS-enforced outbound network deny for the sandbox executable on the target Windows EVM.

Mechanism:
- Windows Defender Firewall temporary outbound block rule;
- scoped to the exact .venv Python executable used by the sandbox test;
- baseline connectivity to 127.0.0.1:11434 is confirmed before blocking;
- after rule installation, a new socket connection to 127.0.0.1:11434 must fail;
- the temporary firewall rule is removed in a finally block.

Safety:
- requires elevated PowerShell;
- no permanent firewall policy is installed;
- cleanup runs even when the test fails;
- no inbound rules are modified;
- no unrelated executable is targeted.

PASS means NETWORK_ISOLATION_BASELINE only.
It does not by itself prove restricted token/AppContainer or filesystem ACL confinement.
