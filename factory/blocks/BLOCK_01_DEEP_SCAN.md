# Deep Agent Scan

Standalone READ-ONLY cross-check for BLOCK-01.

Purpose: find agent-like projects that do not necessarily contain files named `agent.yaml` or `AGENTS.md`.

Signals:
- project structure markers (README, pyproject, package.json, requirements);
- strong agent markers (role, capabilities, prompt, RAG, KB, tools, permissions, evals);
- weaker workflow/planner/executor/autopilot/copilot markers.

Run all available drives:

```powershell
python scripts/deep_agent_scan.py --out .father/deep-agent-scan.json
```

Run selected roots first:

```powershell
python scripts/deep_agent_scan.py G:\1 F:\FATHER_MODELS --out .father/deep-agent-scan.json
```

This script does not modify discovered projects.
