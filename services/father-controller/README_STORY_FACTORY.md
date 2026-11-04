# FATHER Story Factory v1

Single-LLM creative-writing product.

## Candidate league
- `ministral-3:8b` — current Mistral-recommended replacement for the deprecated Mistral Small Creative path; local Ollama candidate.
- `qwen2.5:7b` — current baseline already installed.
- `mistral-nemo` — 12B local challenger.

Only one model is active in Story Agent at a time.

## Flow
1. `PREPARE_FATHER_STORY_MODELS.ps1` — ensure local candidates exist.
2. `RUN_FATHER_STORY_BENCH.ps1` — run identical story tasks.
3. Read `evidence/story_model_bench_latest.json` side by side.
4. `SELECT_FATHER_STORY_MODEL.ps1 -Model "ministral-3:8b"` (or another candidate).
5. `START_FATHER_STORY_STUDIO.ps1`.

No model is automatically promoted on latency alone; artistic quality requires side-by-side review.
