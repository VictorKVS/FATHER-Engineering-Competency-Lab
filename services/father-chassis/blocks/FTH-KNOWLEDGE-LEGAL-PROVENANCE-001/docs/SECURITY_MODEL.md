# Security Model
Owner: Security Architect / DevSecOps.

Threats:
- declared rights escalation;
- forged policy evidence;
- source substitution after approval;
- policy downgrade;
- prompt-induced approval;
- provenance mismatch.

Controls:
- deterministic policy;
- policy id/version recorded;
- evidence hash/ref required;
- source content hash bound to provenance;
- deny-before-allow;
- UNKNOWN -> HOLD;
- no LLM authority in approval path;
- immutable decision/provenance.

Future:
signed policy releases, signed evidence, jurisdiction packs, revocation lists.