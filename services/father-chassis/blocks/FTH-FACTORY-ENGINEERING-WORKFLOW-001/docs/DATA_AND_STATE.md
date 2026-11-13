# Data and State
Owner: System Analyst + Data Architect.

Namespace: factory_engineering_workflow
Key: workflow_id

Snapshot schema version: 1.

Persisted:
- approved/accepted artifacts;
- stage history including BLOCKED results;
- workflow_id.

Static StageDefinitions are code/version contract and are not duplicated as mutable state.

Integrity:
every restored StageArtifact hash must equal a fresh hash computed from semantic fields.

Consistency:
persist occurs after each accepted external artifact and after each stage result.

Open:
atomic compare-and-swap and multi-writer concurrency not yet supported.