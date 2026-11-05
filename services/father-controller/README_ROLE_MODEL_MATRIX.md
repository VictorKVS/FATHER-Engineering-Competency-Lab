# FATHER Role Model Matrix MVP-01

Core rule: there is no globally best LLM. A model is admitted and ranked per role.

Current role lanes:
- TEXT_ANALYST
- REASONING
- CODING
- CREATIVE_WRITING
- EDGE_FAST
- VISION

Routing order:
`ROLE -> RELIABILITY GATE -> QUALITY GATE -> THERMAL POLICY -> VALUE SCORE -> MODEL`

Important:
- qwen2.5:3b is the current TEXT_ANALYST champion candidate from local value evidence.
- llama3.2:1b remains FAST/EDGE; it is not promoted to analyst champion because it misses the current analyst quality gate.
- ministral-3:8b remains a CREATIVE_WRITING candidate. Its analytical reliability failure does not remove it from the creative lane.
- REASONING, CODING, CREATIVE and VISION roles still require their own role-specific acceptance benches.

This matrix intentionally does not replace Stage29 production routing until the new role router passes locally.

Run:
```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_ROLE_MODEL_MATRIX_MVP01.ps1
```
