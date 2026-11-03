# FATHER Chassis v2.0 / Stage 11

Stage 11 proves the first consolidated workflow line:

event -> router -> agent/tool -> state -> audit -> result

Checks:

- API input routed to the IB agent and completed
- File input routed to the general agent
- deterministic Tool Slot step executes inside the workflow
- explicit state transition order is verified
- every transition is written to JSONL audit
- a failed tool stops the workflow before the agent executes
- task quality remains deterministic and testable

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE11.ps1
