# Security Model
Owner: Security Architect / DevSecOps.

Threats:
- hallucinated facts;
- evidence-free entities;
- dangling relation references;
- prompt injection affecting extraction schema;
- extractor-version drift;
- silent confidence changes.

Controls:
- deterministic reference extractor;
- explicit policy/version;
- evidence chunk required;
- relation referential integrity;
- confidence explicit;
- unsupported patterns produce no facts;
- canonical hashes.

Future:
LLM extractor sandbox, schema validation, calibration datasets, confidence calibration.