# FUA-001 Windows Process Sandbox Baseline v0.1

This stage moves block 20 beyond policy-only checks into a real child-process boundary on the Windows target EVM.

Implemented:
- explicit executable allowlist;
- shell=False;
- isolated temporary working directory;
- minimal scrubbed environment;
- stdin disabled;
- stdout/stderr capture with maximum retained size;
- execution timeout;
- Windows Job Object with KILL_ON_JOB_CLOSE to terminate the assigned process when the sandbox job closes.

Not yet claimed:
- network namespace/firewall isolation;
- low-integrity/restricted token;
- filesystem ACL/AppContainer boundary;
- container/VM isolation;
- hostile native-code containment.

Therefore this gate is PROCESS_ISOLATION_BASELINE, not FINAL_SANDBOX_CERTIFIED.
