# Operations Runbook
Owner: DevSecOps/SRE.

Operational rule:
artifact schema version is part of persisted state compatibility.

Before deploy:
- run full regression;
- run typed roundtrip tests;
- verify existing snapshots use supported schema versions.

On unsupported persisted version:
fail startup explicitly; do not discard state.

Upgrade:
ship migration adapter before increasing schema version.

Rollback:
verify old release understands all persisted artifact schema versions before rollback.