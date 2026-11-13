# Architecture
Owner: Principal/Solution Architect.

Customer/Agent artifacts
        ↓
FactoryEngineeringWorkflow(workflow_id)
        ├─ StageDefinitions (static contract)
        ├─ artifacts[type]
        ├─ history[]
        └─ StateStore
             namespace=factory_engineering_workflow
             key=workflow_id

Restore path:
StateStore -> snapshot -> typed StageArtifact reconstruction -> hash validation -> history reconstruction -> available_stage.

Authority:
Orchestrator owns stage progression; LLM agents do not.

Replaceability:
StateStore backend is replaceable; workflow semantics are not.