# FATHER Factory Engineering Orchestration

## Rule

No role starts because a task "looks ready".

A role starts only when the workflow has the exact approved upstream artifacts required by its contract.

## Execution chain

```text
APPROVED CUSTOMER REQUEST
        ↓
BUSINESS_ANALYSIS
        ↓ BusinessProcessSpec
SYSTEM_ANALYSIS
        ↓ SystemAnalysisPackage
ALGORITHM_SELECTION
        ↓ AlgorithmSpec
ARCHITECTURE
        ↓ ArchitectureSpec
TEST_ARCHITECTURE
        ↓ TestContract
DEVELOPMENT_PACKET
        ↓ DevelopmentPacket
IMPLEMENTATION
        ↓ ImplementationChange
DELIVERY
        ↓ DeliveryQualification
QUALIFICATION
        ↓ QualificationDecision
```

## Hard gates

- developer cannot start before DevelopmentPacket;
- test architect cannot start before architecture + algorithm + system analysis;
- DevSecOps cannot start before implementation + architecture + test contract;
- Qualification Auditor cannot start before delivery evidence + test contract;
- wrong role cannot publish another role's artifact;
- unapproved artifact does not unlock downstream work;
- stage order cannot be skipped.

## Traceability

Every artifact is hash-addressed.

Workflow state contains:
- artifact ID;
- artifact type;
- producer agent;
- approval state;
- artifact hash;
- evidence references;
- stage result;
- blockers.

This lets future Trust/Competency bind:
`agent → artifact → evidence → qualification`.

## Future execution

The orchestrator is intentionally independent from LLM prompts.

Later, each stage will execute as:

```text
stage contract
+ agent role contract
+ qualified KB release
+ current upstream artifacts
+ tools
+ prompt
    ↓
agent result
    ↓
schema validation
    ↓
specialist review / automated checks
    ↓
approved StageArtifact
    ↓
next stage
```

The orchestrator owns workflow authority. The LLM does not.
