# Operations Runbook
Owner: DevSecOps/SRE.

Default local persistence: SQLite StateStore.
Production-capable persistence: PostgreSQL StateStore when configured.

Checks:
- StateStore readable/writable;
- known registration restored after reopen.

Incident rule:
product/version conflict must never be overwritten; escalate to Architect + Qualification Auditor.

Backup/restore: inherited from StateStore backend.
Schema upgrade requires migration plan.
Rollback must preserve existing namespace data unless an approved migration says otherwise.