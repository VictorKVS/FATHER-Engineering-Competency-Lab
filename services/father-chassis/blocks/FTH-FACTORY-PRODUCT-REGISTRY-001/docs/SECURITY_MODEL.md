# Security Model
Owner: Security Architect / DevSecOps.

Assets: product identity, recipe hash, version history.

Threats:
- silent overwrite;
- product/version collision;
- tampered state;
- unauthorized mutation;
- stale/malformed record.

Controls:
- fail-closed recipe hash conflict;
- deterministic key;
- immutable ProductRegistration;
- controlled StateStore boundary;
- qualification evidence.

Not yet implemented:
signature/attestation, registry mutation authorization, distributed transaction control.