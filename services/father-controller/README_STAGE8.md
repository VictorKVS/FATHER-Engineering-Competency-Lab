# FATHER Chassis v1.7 / Stage 8

Stage 8 turns the F: storage failure into a permanent factory guard.

The preflight verifies before agent execution:

- OLLAMA_MODELS is set and the storage path exists
- model storage has at least 20 GiB free
- Ollama /api/tags is reachable
- every model required by config/brains.json is installed

It also runs two negative controls:

1. a deliberately missing storage path must be rejected
2. a deliberately missing model must be rejected

Only after the positive preflight passes is an agent allowed to assemble/use its Brain.

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE8.ps1

Evidence:

    services\father-controller\evidence\stage8_evidence.json
