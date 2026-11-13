# Interfaces and Variables
Owner: Architect + System Analyst.

Constructor:
FactoryEngineeringWorkflow(catalog=None, store=None, workflow_id="default")

Variables:
- workflow_id: str, required non-empty;
- store: StateStore|null;
- artifact.artifact_id: str;
- artifact.artifact_type: str;
- artifact.producer_agent_id: str;
- artifact.payload: dict;
- artifact.approved: bool;
- artifact.evidence_refs: tuple[str,...];
- artifact.artifact_hash: SHA-256 hex.

Persistence snapshot:
{
 schema_version,
 workflow_id,
 artifacts,
 history
}

Public operations remain:
add_external_artifact()
available_stage()
submit_stage_artifact()
status()
workflow_hash()

Errors:
ValueError on invalid workflow_id, malformed snapshot, artifact hash mismatch, unavailable stage.
KeyError on unknown stage.