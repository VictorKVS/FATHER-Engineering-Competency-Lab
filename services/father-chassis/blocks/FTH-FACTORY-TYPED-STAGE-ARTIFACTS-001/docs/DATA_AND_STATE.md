# Data and State
Owner: System Analyst + Data Architect.

Persisted artifact representation v1 (inside workflow snapshot schema v2):
{
  artifact_id,
  artifact_type,
  payload_schema_version,
  producer_agent_id,
  payload_data,
  approved,
  evidence_refs,
  artifact_hash
}

Rules:
- payload_data is serialization only, never the runtime model;
- runtime payload is reconstructed as the registered typed class;
- schema version is mandatory;
- artifact hash covers payload_schema_version and payload_data;
- unknown future version is rejected unless migration adapter exists.

Migration:
v1 -> future versions through explicit per-artifact migration adapters.
No silent field dropping or default injection across versions unless approved by schema migration contract.

## Workflow snapshot compatibility

Typed artifact persistence changes the outer workflow snapshot format from schema v1 to schema v2.

- snapshot v1 = legacy generic payload representation;
- snapshot v2 = typed payload_data + payload_schema_version.

No silent v1 -> v2 coercion is permitted because legacy arbitrary dict payloads do not contain enough semantic guarantees to reconstruct approved typed contracts. A v1 snapshot therefore fails closed and requires an explicit migration/restart decision.
