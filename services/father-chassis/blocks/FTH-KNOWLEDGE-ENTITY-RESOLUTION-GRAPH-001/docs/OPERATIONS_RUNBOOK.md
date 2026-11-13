# Operations Runbook
Owner: DevSecOps/SRE.

Health:
resolution policy version available; graph builder deterministic.

Upgrade:
policy change requires rebuilding graph snapshot from immutable K5 extraction sets.

Incident:
dangling endpoint/conflict policy violation -> reject or explicit conflict, never silent merge.

Rollback:
regenerate with prior graph policy version.