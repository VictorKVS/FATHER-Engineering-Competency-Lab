# NEXUS 000-100 — Military / OKR Discipline Overlay

This overlay imports the **discipline** of classical staged defense development and
formal systems engineering into NEXUS/FATHER. It does not claim certification or
formal compliance with a military standard.

## Core rule

No next major baseline is entered merely because implementation exists.

A transition requires:

INPUT -> WORK -> REVIEW -> TEST -> EVIDENCE -> ACCEPTANCE -> BASELINE

## Mapping

| NEXUS | Engineering meaning | Classical analogue |
|---|---|---|
| 000-009 | Need, TZ, requirements | Mission/requirements review |
| 010-019 | Preliminary architecture | Sketch/preliminary design |
| 020-039 | Detailed design and working configuration | Technical design / working documentation |
| 040-049 | Integrated prototype | Prototype/system integration |
| 050-069 | Security and test readiness | Test readiness |
| 070-079 | Qualification / preliminary tests | Preliminary/qualification tests |
| 080-089 | Operational readiness | Readiness for operation |
| 090-099 | Independent acceptance / Polygon | Acceptance/state/interdepartmental testing |
| 100 | Proven operation | Accepted product in operation |

## Baselines

1. REQUIREMENTS_BASELINE
2. DESIGN_TO_BASELINE
3. BUILD_TO_BASELINE
4. AS_BUILT_BASELINE
5. TEST_BASELINE
6. VERIFIED_BUILD_BASELINE
7. OPERATIONAL_BASELINE
8. ACCEPTED_RELEASE_BASELINE
9. PRODUCTION_PROVEN_BASELINE

Each baseline is immutable after approval. Changes after approval require a new
version plus recorded disposition and regression.

## Modern additions

The old discipline is retained, but the proof package is modernized:

- Git commit SHA
- CI workflow run
- SBOM
- dependency/security scans
- artifact hashes
- signed provenance/attestation when available
- agent/model/prompt/RAG/KB versions
- evaluation evidence
- Polygon result
- production telemetry

This is the NEXUS equivalent of "documentation + prototype + tests + acceptance
act", adapted to AI/LLM systems.
