# Operations Runbook
Owner: DevSecOps/SRE.

Health:
policy registry available; evaluator deterministic; provenance store available.

Incident:
policy/evidence mismatch -> HOLD or REJECTED; never fallback to parser.

Upgrade:
new policy version must be explicit; prior decisions remain bound to original policy version.

Rollback:
restore previous policy version only for new decisions; historical decisions remain immutable.