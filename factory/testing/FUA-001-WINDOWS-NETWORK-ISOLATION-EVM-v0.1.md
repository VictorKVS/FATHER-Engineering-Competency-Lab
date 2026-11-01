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


## v0.2 test correction

The first target-EVM run used 127.0.0.1:11434 as the deny target. That is not sufficient evidence for ordinary outbound egress isolation because Windows treats loopback as a distinct filtering/IPC scenario.

The corrected EVM test:
1. finds a reachable external TCP endpoint before the firewall rule;
2. records that exact host/port;
3. installs the temporary program-scoped outbound block;
4. requires a new connection from the same Python executable to the same external endpoint to fail;
5. removes the rule in finally.

Loopback/Ollama connectivity is no longer used as the proof target for external egress isolation.
