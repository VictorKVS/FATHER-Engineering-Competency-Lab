# EXP-BREAKOUT-B1 — sealed treatment passport

- **What:** prepare the treatment arm for the first Breakout transfer comparison.
- **Why:** measure whether approved factory knowledge improves an unfamiliar task relative to the sealed A1 baseline.
- **Alternatives:** expose all Pong artifacts; summarize patterns in the prompt; add only versioned PAT/ANTI snapshots.
- **Decision:** reuse the byte-identical task, budgets and result schema; add only `PAT-GAME-0001.md` and `ANTI-GAME-0001.md`.
- **Why chosen:** the automatic pair diff can attribute the supplied-context difference to two named factory assets.
- **Constraints:** same provider/model/version, 45 minutes, three iterations, local tools, network disabled, distinct fresh context IDs.
- **Risks:** provider pretraining remains uncontrolled; small samples have low statistical power; agents may cite patterns without applying them.
- **Evidence:** packet hashes, source-snapshot hashes, reproducible archives, A/B-diff output, future paired results and reviews.
- **Version/status:** 0.1.0 / sealed, not executed.
- **Links:** `EXP-BREAKOUT-A1`, `PAT-GAME-0001`, `ANTI-GAME-0001`, `XFER-PY-PONG-0001`, `BENCH-GAME-10-0001`.
- **Result:** treatment packet accepted for paired scheduling only; no competence or golden-pattern conclusion exists.
