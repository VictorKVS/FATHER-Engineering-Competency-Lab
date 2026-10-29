# TEST-01 — Story Model Swap

Purpose: prove that one fixed agent/profile can run on interchangeable LLMs while keeping Prompt, RAG, KB, contracts and tests constant.

## Run locally

```powershell
Set-Location 'G:\1\FATHER-Engineering-Competency-Lab-git'
git pull
father-factory test-01-story-model-swap
```

To publish the resulting evidence package to the current Git branch:

```powershell
father-factory test-01-story-model-swap --publish
```

## Fixed

- AG-001
- ALINA_LITERARY
- STORY_CONTINUATION
- Prompt v0.2.0
- RAG ALINA_LITERARY_RAG_V02
- KB v0.2.0
- same input/output contract
- same automatic gate

## Variable

Only `model_id`.

## Failover

Candidate 1 -> runtime/contract/score gate -> PASS: select.
If FAIL -> stop model -> candidate 2 -> repeat.
If none pass -> HOLD.

## Evidence

Each run writes:

- summary.json
- leaderboard.json
- selected_model.json
- REVIEW_BUNDLE.md
- per_model_evidence/*.json

The automatic gate proves machine-checkable conformance. Literary quality remains a separate quality-review gate.
