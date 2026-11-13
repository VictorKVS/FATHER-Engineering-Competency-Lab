# Security Model
Owner: Security Architect / DevSecOps.

Assets:
artifact semantics, field integrity, producer/approval binding, persisted workflow history.

Threats:
- field injection;
- type confusion;
- schema downgrade;
- unknown-field semantic drift;
- persisted payload tampering;
- artifact_type spoofing.

Controls:
- static artifact schema registry;
- exact payload class validation;
- explicit schema version;
- fail-closed unknown type/version;
- deterministic SHA-256 over envelope + typed serialization;
- hash verification after typed deserialization.

Future:
signed schema releases and artifact attestations.