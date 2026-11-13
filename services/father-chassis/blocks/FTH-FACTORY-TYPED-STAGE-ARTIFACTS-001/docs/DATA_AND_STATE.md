# Data and State
Owner: System Analyst + Data Architect.

Persisted artifact representation v1:
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