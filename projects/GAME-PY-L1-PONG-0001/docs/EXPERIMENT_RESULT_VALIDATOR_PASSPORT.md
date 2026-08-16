# EXP-RESULT-VALIDATOR-0001 — result validation passport

- **What:** reject incomplete, internally inconsistent or incomparable A/B execution records before scoring transfer.
- **Why:** sealed prompts control supplied context, but do not make runner identity, timing, metrics or evidence trustworthy by themselves.
- **Alternatives:** manual spreadsheet review; accept self-reported JSON; strict machine gate followed by independent review.
- **Decision:** validate each record, then validate pair compatibility; keep truthfulness/provenance review as a separate mandatory stage.
- **Why chosen:** deterministic rejection rules prevent missing fields and changed budgets from silently entering the learning corpus.
- **Constraints:** provider/model/version must match; contexts and packet hashes must differ; budget is fixed; completed records require hashes, timing, metrics, test and compile evidence.
- **Risks:** syntactically valid evidence can still be fabricated; timestamps and token usage are runner-reported; provider version strings may be ambiguous.
- **Evidence:** `factory/result_validator.py`, `tests/test_result_validator.py`, `EXP-RESULT-CONTRACT-0001`, future signed execution records.
- **Version/status:** 0.1.0 / accepted for execution intake.
- **Links:** `EXP-BREAKOUT-A1`, `EXP-BREAKOUT-B1`, `XFER-PY-PONG-0001`, `BENCH-EVAL-0001`.
- **Result:** validation permits evaluation but never asserts that execution occurred, that treatment won, or that a role/model improved.
