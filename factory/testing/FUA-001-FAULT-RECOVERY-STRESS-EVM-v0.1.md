# FUA-001 Fault / Recovery Stress EVM v0.1

Purpose:
prove repeatable recovery behavior and fail-closed security behavior on the target EVM.

The gate verifies:
- 100/100 transient failures recover exactly on the bounded third attempt;
- 100/100 PermissionError security denials are never retried;
- 50/50 audit chains verify before mutation and fail after mutation;
- 100/100 evidence records verify before mutation and fail after payload mutation.

PASS does not grant production readiness.
HUMAN_ACCEPTANCE remains separate.
