# EXP-BREAKOUT-A1 — sealed baseline passport

- **What:** prepare the first clean Breakout baseline measurement without transferring Pong implementation knowledge.
- **Why:** the current development context has already seen `PAT-GAME-0001`; using it as baseline would inflate the apparent value of factory memory.
- **Alternatives:** reuse the current context; trust a verbal promise; isolate and hash the exact allowed context.
- **Decision:** distribute only `TASK.md`, `result-template.json` and a cryptographic manifest; require a context inventory preflight before execution.
- **Why chosen:** it makes accidental reference leakage visible and keeps the A arm reproducible across providers.
- **Constraints:** 45 minutes, three iterations, local Python tools, no network/retrieval, model/version/token usage recorded.
- **Risks:** a hidden model may already know generic Pong/Breakout patterns; operator attestation cannot prove undocumented provider-side context; hashes prove packet identity, not model purity.
- **Evidence:** packet hashes, deterministic archive checksum, preflight result, future source/tests/reviews and completed result record.
- **Version/status:** 0.1.0 / sealed, not executed.
- **Links:** `BENCH-GAME-10-0001`, `XFER-PY-PONG-0001`, future `EXP-BREAKOUT-B1`.
- **Result:** baseline packet may be scheduled in a fresh context; no experimental or competence conclusion exists yet.

This control is model-agnostic: different providers may participate, but paired comparisons must record and hold model/version, budgets and tool permissions constant. It controls supplied context, not pretraining data.
