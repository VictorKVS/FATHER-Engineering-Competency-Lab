# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR IMPLEMENTATION DESIGN, pending adapter packaging check.

Approved semantics:
- do not duplicate Trust CompetencyEvaluator;
- Trust core does not import FATHER;
- FATHER-side gate may depend on narrow Trust adapter/protocol;
- stage policy is explicit and versionable;
- missing/unknown/insufficient competency is BLOCK;
- admission output preserves evidence trace;
- competency is necessary but never sufficient for execution.

Implementation targets:
services/father-chassis/src/father/engineering/competency_admission.py
services/father-chassis/tests/test_competency_admission.py
orchestrator integration after role/stage selection.

Packaging constraint:
before hard importing trust_competency, define a reproducible installation/import mechanism for sibling Trust project.
No sys.path hacks in production code.