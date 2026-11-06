# BLOCK-01 Deep Scan V2

Purpose: reduce false positives from the broad V1 scan.

V2 classifies candidates as:
- AGENT
- AGENT_ASSET
- AGENT_CANDIDATE
- DOCUMENTATION

A real agent candidate needs structural evidence, not only words such as "agent" or "prompt".

Strong structural evidence:
- agent manifest (agent.yaml / AGENTS.md / equivalent);
- executable/runtime files;
- project manifest plus agent/runtime markers.

Documentation, tutorial, reference, tests and knowledge-only folders are penalized unless they contain real executable agent structure.

Recommended comparison run:

```powershell
python scripts/deep_agent_scan_v2.py G:\1 F:\FATHER_MODELS --out .father\deep-agent-scan-v2.json
```
