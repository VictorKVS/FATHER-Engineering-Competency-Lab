# Operations Runbook
Owner: DevSecOps/SRE.

Health:
validator available; SHA-256 hashing operational; registry available.

Incident:
hash/metadata conflict -> preserve both records and escalate; never overwrite silently.

Resource protection:
production adapters must enforce size/time limits before hashing very large sources.

Backup/restore:
inherits future source-registry storage.

Upgrade:
record schema changes require version/migration plan.