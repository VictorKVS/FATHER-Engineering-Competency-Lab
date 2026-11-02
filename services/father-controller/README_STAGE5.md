# FATHER Chassis v1.4 — Stage 5

Adds deterministic, task-specific quality scoring.

No LLM judge is used.

For every test case the Competency Pack can define:
- required concept groups;
- forbidden terms/known bad patterns;
- min/max response length;
- pass threshold.

The Model Zoo DB now stores:
- quality_score
- quality_passed
- scorer
- scoring details

Ranking order:
1. average deterministic quality score;
2. quality pass rate;
3. latency.

This still does not claim universal model intelligence.
Scores are valid only for the specific task suite and competency pack used.

Run:
```powershell
.\RUN_FATHER_STAGE5.ps1
```
