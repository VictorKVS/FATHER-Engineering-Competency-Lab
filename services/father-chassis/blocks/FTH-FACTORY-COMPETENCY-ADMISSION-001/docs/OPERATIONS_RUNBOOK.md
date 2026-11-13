# Operations Runbook
Owner: DevSecOps/SRE.

Precondition:
Trust Competency package/adapter available through reproducible installation.

Health:
- stage policy registry load succeeds;
- Trust adapter responds;
- qualification engine returns structured decision.

Failure:
adapter unavailable -> admission BLOCKED, never bypassed.

Upgrade:
changes to C-level semantics belong to Trust project and require compatibility review.

Rollback:
FATHER release must match installed Trust adapter/API version.

No manual override of competency result without a separately audited human-exception mechanism.