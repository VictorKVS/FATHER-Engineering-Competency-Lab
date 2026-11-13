# Security Model
Owner: Security Architect / DevSecOps.

Assets:
stage authority, competency claims, evidence linkage, qualification result.

Threats:
- role impersonation;
- fake claimed level;
- missing evidence treated as success;
- competency downgrade policy;
- stale evidence;
- adapter bypass;
- one gate substituting for another.

Controls:
- fail-closed evaluation;
- existing Trust C0-C6 LEVEL_ORDER;
- evidence count/type requirements;
- claim domain/capability matching;
- independent role + competency gates;
- reasons/evidence IDs preserved;
- Trust core remains authoritative evaluator.

Not yet covered:
evidence freshness policy, signature validation, persistent ledger adapter, competency revocation.