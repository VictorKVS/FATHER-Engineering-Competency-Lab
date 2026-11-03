# FATHER Chassis v2.8 / Stage 19

Stage 19 creates a release manifest for the physically verified FATHER factory state.

The manifest records:

- release/chassis version
- verified stage number
- Model Zoo brain definitions
- Agent Zoo manifests
- routing table
- policy/UAG configuration
- externally committed GitHub anchor
- manifest integrity digest

The compatibility matrix verifies:

- every agent references an existing brain
- every routed agent exists
- every agent has a policy profile
- external anchor commit/head are present
- current runtime preflight still passes

Negative controls prove detection of:

- missing brain
- missing policy
- modified release manifest

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE19.ps1
