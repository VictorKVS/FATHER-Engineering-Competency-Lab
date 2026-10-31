# GitHub-native Factory Integration

NEXUS/FATHER does not replace GitHub.

## Responsibilities

### NEXUS/FATHER
- stage engine 000-100
- product/system design
- specialist orchestration
- agents, models, tools and knowledge
- tests, evidence and traceability
- release/Polygon lifecycle

### GitHub
- source versioning
- pull requests
- reusable CI workflows
- branch/ruleset enforcement
- release history
- workflow run identity
- future artifact attestations and provenance

## Golden path

Idea -> Project Scaffold -> GitHub -> Reusable CI -> Stage Evidence -> Release Candidate -> Polygon -> Production

## Current implementation level

Implemented:
- reusable factory CI
- canonical evidence schema
- five macro phases over 000-100
- demo autopilot 000-100

Foundation only, not yet production-proven:
- SBOM generation
- GitHub artifact attestation
- SLSA provenance
- GitHub Environment approvals
- release rulesets

These capabilities must not be marked PASS until a real GitHub workflow produces and verifies the evidence.
