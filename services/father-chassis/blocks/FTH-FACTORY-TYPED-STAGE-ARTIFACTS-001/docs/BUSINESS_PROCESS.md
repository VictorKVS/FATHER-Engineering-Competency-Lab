# Business Process
Owner: Senior Business Analyst.

Goal:
ensure every engineering handoff has an explicit meaning, structure and owner so downstream roles never infer semantics from arbitrary dictionaries.

Before:
StageArtifact.payload accepts dict[str, Any].

After:
each stage output uses a declared payload schema bound to artifact_type.

Value:
- fewer integration ambiguities;
- easier automated validation;
- safer persistence/migration;
- stronger traceability;
- lower risk of developer-invented fields.

KPIs:
- untyped cross-stage payload acceptance: 0%;
- artifact_type/payload mismatch rejection: 100%;
- round-trip serialization fidelity: 100%;
- unknown schema version rejection: 100%.