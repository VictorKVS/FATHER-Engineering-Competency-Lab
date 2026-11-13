# Security Model
Owner: Security Architect / DevSecOps.

Assets:
stage authority, approved artifacts, workflow history, evidence references.

Threats:
- restart resets governance;
- persisted artifact tampering;
- workflow-id collision;
- stage skipping;
- wrong-role output;
- unapproved artifact injection.

Controls:
- workflow_id isolation;
- fail-closed admission;
- producer ownership check;
- approval requirement;
- SHA-256 artifact integrity verification on restore;
- StateStore boundary.

Not yet covered:
cryptographic signature/attestation of snapshot; distributed locking; actor identity on artifact approval.