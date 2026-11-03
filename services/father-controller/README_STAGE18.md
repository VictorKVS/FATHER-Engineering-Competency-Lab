# FATHER Chassis v2.7 / Stage 18

Stage 18 turns the Stage 17 anchor into an externally committed GitHub anchor.

The exact Stage 17 anchor values are stored in:

    config/anchors/stage17_anchor_committed.json

and were committed to GitHub in:

    c5f69c6abc739d8187c3ed293fed7d75a4b28d2a

Release checks:

- local Stage 17 anchor exists
- GitHub-committed anchor exists after sync from origin/main
- local and committed values match exactly
- the repository can resolve the Git commit that introduced the anchor file
- the resolved commit matches the expected external anchor commit
- simulated local modification is detected by comparison
- simulated local rollback is detected by comparison

This proves an external Git/GitHub anchor reference. It is still not a trusted timestamp authority or legal digital signature.

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE18.ps1
