# FATHER Text Analyst Exam v1

Purpose: distinguish superficial summarization from deep text analysis.

The exam is generated from:
- universal analytical questions;
- hallucination traps;
- Knowledge Base tasks;
- structured variants;
- book-specific questions based on ingested metadata.

Target: ~150 analytical prompts per book.

## Levels
- L1 direct fact
- L2 multi-fragment fact
- L3 causality / relationships / epistemics
- L4 continuity / interpretation / forecast

## Grading dimensions
- factual accuracy
- source grounding
- causal reasoning
- epistemic accuracy
- continuity
- KB structure
- uncertainty handling
- hallucination resistance
- depth
- latency

Unknown or unsupported claims must use:
`НЕ ПОДТВЕРЖДЕНО ТЕКСТОМ`

## Build
```powershell
.\RUN_FATHER_TEXT_ANALYST_EXAM_BUILD.ps1
```
