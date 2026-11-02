# FATHER Chassis v1.5 — Stage 6

Purpose: prove that a Competency Pack's knowledge is actually delivered to the agent before interpreting model rankings.

Changes:
- FolderKnowledge now has an explicit fallback mode for small bootstrap packs.
- Retrieval mode is surfaced in AgentResult metadata.
- Stage PASS requires a deterministic knowledge probe.
- Stage PASS requires knowledge delivery to all tested brains.
- Stage PASS requires at least one brain to pass the IB rubric.

This fixes the Stage 5 release-gate weakness where the stage could report PASS even if all IB quality tests failed.

Run through the repository updater:

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab
.\FATHER_UPDATE.ps1
```
