# FATHER Chassis v2.5 / Stage 16

Stage 16 adds an authenticated checkpoint for the Evidence Ledger head.

It uses HMAC-SHA256 with a separate secret to authenticate:

- current ledger entry count
- current ledger head hash
- current ledger validity state

Release checks:

- existing Stage 15 ledger is valid
- authenticated checkpoint verifies
- modifying checkpoint content is detected
- verifying with the wrong secret is rejected
- rolling the ledger back to an older state is detected
- restoring the original ledger makes the checkpoint valid again

Important: this is an authenticated checkpoint, not an asymmetric digital signature and not an external timestamp/notary service.

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE16.ps1
