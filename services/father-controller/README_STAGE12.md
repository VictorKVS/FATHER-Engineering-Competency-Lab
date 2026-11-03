# FATHER Chassis v2.1 / Stage 12

Stage 12 introduces the first policy/UAG gate around the workflow.

Policy is evaluated before agent execution and before tool execution.

Release checks:

- policy registry health
- allowed general-agent calculator path completes
- IB agent is denied calculator access
- IB agent is denied an architecture task by policy
- valid IB task without a forbidden tool still completes
- all policy decisions are written to audit
- denied tool execution stops before tool and agent execution

This is a bootstrap policy gate, not the final production UAG.

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE12.ps1
