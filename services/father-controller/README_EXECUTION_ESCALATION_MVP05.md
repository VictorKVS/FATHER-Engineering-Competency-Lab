# FATHER Execution Telemetry + Automatic Escalation MVP-05

Goal: prove the first controlled automatic escalation path:

`qwen2.5:3b -> acceptance gate -> qwen2.5:7b`

This MVP deliberately does **not** claim semantic quality judging. The
acceptance gate uses only verifiable runtime criteria:

- runtime success/error;
- minimum answer length;
- optional required terms.

Telemetry records for every attempt:

- brain_id;
- runtime model;
- latency_ms;
- content_chars;
- error;
- router source;
- fallback flag;
- acceptance result and rejection reasons.

Only the already proven TEXT_ANALYST path is promoted for escalation.
Other roles remain blocked/fallback-controlled until role-specific benches.

The test includes one normal accepted 3B answer and one intentionally strict
acceptance threshold to deterministically exercise the 3B -> 7B escalation
mechanism.

Run:

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_EXECUTION_ESCALATION_MVP05.ps1
```
