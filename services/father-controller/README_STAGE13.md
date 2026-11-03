# FATHER Chassis v2.2 / Stage 13

Stage 13 adds a bootstrap execution sandbox between Policy/UAG and ToolRegistry.

This is not an OS/container sandbox yet. It is a controlled execution boundary that proves the architectural seam.

It enforces:

- allowlisted sandboxed tools
- argument schema restrictions
- numeric limits
- text-size limits
- execution timeout
- audit of sandbox decisions

Release checks:

- valid calculator call succeeds
- unknown tool is blocked before ToolRegistry and Agent
- excessive numeric argument is blocked
- Policy denial happens before Sandbox
- sandbox allow/block decisions are written to audit

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE13.ps1
