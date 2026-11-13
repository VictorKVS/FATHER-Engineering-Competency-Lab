# Security Model
Owner: Security Architect / DevSecOps.

Threats:
- parsing source that was not approved;
- provenance/source substitution;
- malicious encoding/binary input;
- parser ambiguity;
- hidden content injection;
- oversized input resource exhaustion.

Controls:
- require APPROVED decision;
- verify provenance binding before parse;
- explicit media type;
- strict UTF-8 in v1;
- deterministic parser/version;
- diagnostics on partial/reject;
- production size limits required for adapters.

Future:
format sandboxing, malware scan gate, PDF/DOCX parser isolation.