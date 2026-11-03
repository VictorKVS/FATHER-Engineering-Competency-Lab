# FATHER Chassis v2.6 / Stage 17

Stage 17 creates an external-anchor artifact for the current trust chain.

The anchor stores:

- ledger entry count
- ledger head hash
- SHA-256 of the authenticated checkpoint file

Release checks:

- Stage 15 ledger is valid
- Stage 16 checkpoint is valid
- anchor verifies against both
- checkpoint-file modification is detected
- ledger rollback/head change is detected
- restored state verifies again

Important: the local stage only creates and verifies the anchor artifact.
Its externalization is achieved when the artifact is committed to GitHub.
This is not a trusted timestamp service and not a legal digital signature.

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE17.ps1
