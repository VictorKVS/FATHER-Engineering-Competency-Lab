# Security Model
Owner: Security Architect / DevSecOps.

Threats:
- path/URL spoofing;
- mutable source under same locator;
- metadata injection;
- malicious oversized input;
- declared rights falsely treated as approval.

Controls:
- SHA-256 content fingerprint;
- immutable intake record;
- locator retained separately from content hash;
- declared rights/access explicitly non-authoritative;
- size/resource limits required for production adapters;
- no automatic legal approval.

Future:
malware scanning, MIME/type validation, signature verification, quarantine.