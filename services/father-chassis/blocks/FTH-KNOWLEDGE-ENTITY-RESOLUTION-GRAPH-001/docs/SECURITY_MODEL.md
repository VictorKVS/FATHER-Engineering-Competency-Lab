# Security Model
Owner: Security Architect / DevSecOps.

Threats:
- false entity merge;
- name collision;
- type-conflict suppression;
- dangling relation endpoint;
- evidence lineage loss;
- order-dependent graph identity;
- prompt-driven merge decisions.

Controls:
- deterministic v1 resolution policy;
- exact normalized name + same type only;
- type conflicts explicit;
- no LLM merge authority in v1;
- referential integrity validation;
- canonical hashes;
- lineage union preserved.

Future:
review queues, probabilistic resolution, signatures, graph write authorization.