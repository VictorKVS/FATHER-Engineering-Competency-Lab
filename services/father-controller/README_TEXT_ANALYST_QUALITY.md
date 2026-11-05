# FATHER Text Analyst Quality Judge MVP-01

Purpose: evaluate saved qualification answers without rerunning candidate models.

Pipeline:

1. Reliability gate.
2. Deterministic checks: source references, invalid references, uncertainty behavior, answer presence.
3. Semantic judge using the exact RAG context that candidate saw.
4. Quality score.
5. Provisional quality/speed value ranking.
6. Final economy component is added after a metered run.

Default policy:

- Reliability is a gate, not a bonus.
- Final intended value score:
  `0.60 * QUALITY + 0.20 * SPEED + 0.20 * ECONOMY`
- Until energy/cost data exists:
  `0.75 * QUALITY + 0.25 * SPEED`

The LLM judge is not the sole signal. Quality = 80% semantic judge + 20% deterministic checks.

Run:

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_TEXT_ANALYST_QUALITY.ps1
```

Outputs:

- `evidence/text_analyst_quality/quality_partial.json`
- `evidence/text_analyst_quality/quality_latest.json`
