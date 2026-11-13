# Operations Runbook
Owner: DevSecOps/SRE.

Persistence inherits configured StateStore.

Restart:
construct workflow with same workflow_id + store to restore governance state.

Incident:
hash mismatch or malformed snapshot is security/integrity incident; do not auto-heal by discarding state.

Backup/restore:
inherits StateStore backend procedure.

Upgrade:
snapshot schema_version changes require migration path.

Rollback:
old code may not understand future schema versions; deployment must verify compatibility before rollback.