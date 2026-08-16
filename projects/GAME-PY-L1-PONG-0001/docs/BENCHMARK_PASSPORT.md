# BENCH-EVAL-0001 — L1–L10 benchmark passport

- **What:** an executable maturity ladder of ten game-engineering tasks, each with minimum, standard and stretch checkpoints.
- **Why:** task count, code volume and subjective ratings cannot demonstrate that Programmer, Architect or Security Engineer improved.
- **Alternatives:** repeat Pong; accept a senior opinion without rubric; use one opaque aggregate score.
- **Decision:** versioned catalog plus deterministic evaluator, ten shared dimensions and role-specific operational weights.
- **Why chosen:** the same evidence can be rescored transparently for three roles, while mandatory evidence and critical defects remain hard gates.
- **Constraints:** compared arms must use the same model/version, prompt/tool/time budget and task contract. Baseline must not receive internal patterns or reference code.
- **Risks:** benchmark gaming, contaminated context, overfitting to games and false confidence from fewer than three trials.
- **Evidence:** `benchmarks/BENCHMARK-10-GAME-PROGRAMMER.json`, `factory/benchmark_eval.py`, `tests/test_benchmark_eval.py`, future `EXP-*` and `XFER-*` records.
- **Version:** 0.1.0, accepted for trials.
- **Links:** `FATHER-TRAIN-0001`, `PAT-GAME-0001`, `ANTI-GAME-0001`, `XFER-PY-PONG-0001`.
- **Result:** framework accepted; no competence promotion and no parameter-training claim until independent transfer evidence exists.

The evaluator reports task-checkpoint attainment only. Role promotion additionally requires the catalog's multi-task evidence window, unseen transfer and independent Architect, Security and QA reviews.

The present automation context already contains the Pong pattern. It therefore cannot honestly generate the blind Breakout baseline arm. `GAME-PY-L2-BREAKOUT-0002-A1` must run in a fresh isolated context with only the task contract; this is a methodological control, not an implementation blocker.
