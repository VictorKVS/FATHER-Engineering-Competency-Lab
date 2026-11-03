# FATHER Chassis v2.3 / Stage 14

Stage 14 adds a standalone Evidence / Provenance integrity layer.

A completed workflow run is converted into a provenance bundle containing:

- route
- policy decisions
- sandbox decisions
- tool execution
- selected agent / brain / competency
- knowledge sources and retrieval modes
- final result
- audit rows

Each section receives a SHA-256 digest and the bundle receives an aggregate digest.

Release checks:

- the complete workflow run succeeds
- provenance is reconstructable
- route/policy/sandbox/tool/knowledge/result are present
- the original bundle verifies
- changing the result is detected
- removing a required audit stage is detected

This proves integrity checking of evidence artifacts. It is not yet a signed/WORM evidence store.

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE14.ps1
