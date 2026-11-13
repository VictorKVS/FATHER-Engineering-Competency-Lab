# Security Model
Owner: Security Architect / DevSecOps.

Threats:
- model claims knowledge never released;
- stale/unqualified index used silently;
- forged kb_id;
- missing provenance;
- release substitution after qualification;
- prompt injection selecting arbitrary KB.

Controls:
- required KBs derive from immutable agent contract;
- explicit release registry;
- status must be QUALIFIED;
- exact release hash recorded;
- provenance/source-set required;
- retrieval evidence required;
- fail closed on missing release;
- no prompt-controlled release selection in strict mode.

Future:
signed release manifest, freshness/revocation policy, legal-rights evidence verification.