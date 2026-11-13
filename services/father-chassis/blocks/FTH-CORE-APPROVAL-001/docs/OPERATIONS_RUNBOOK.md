# Operations Runbook
Owner: DevSecOps/SRE.

Persistence: runtime StateStore.

Operational checks:
- pending record retrievable;
- approved record retrievable after restart;
- action mismatch rejected;
- protected execution blocked without approval.

Incident rule:
do not manually edit StateStore as a normal approval mechanism.
Use controlled approval interface.

Backup/restore: inherits StateStore procedure.

Future operational additions:
expiry, revocation and approver identity runbooks before those features are enabled.