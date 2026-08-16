# `XFER-PY-PONG-0001` — Functional-core transfer to Breakout

## Passport

- Version/status: 0.2.0 / evaluator available, trials not executed.
- Problem: one successful Pong implementation cannot prove that `PAT-GAME-0001` is reusable.
- Decision: give a fresh Programmer context a small Breakout task while exposing the pattern passport but not Pong implementation code.
- Alternatives: clone/refactor Pong; repeat Pong; transfer directly to a complex game.
- Reason: Breakout changes collision topology and entity count while preserving a small deterministic loop.
- Constraints: Python standard library, headless core, no sound/assets/network/save, maximum 350 non-test source lines.
- Risks: task may accidentally leak Pong code; evaluator may reward superficial structural similarity.
- Evidence required: independent implementation, tests, review, defect log and baseline comparison.
- Related: `PAT-GAME-0001`, `ANTI-GAME-0001`, `LRN-PY-PONG-0001-A01/A02`.

## Transfer task

Build a minimal Breakout core and thin Tkinter adapter with:

1. one player paddle;
2. one ball;
3. at least 3×5 bricks;
4. deterministic collision and brick removal;
5. win/loss states and restart;
6. headless tests for boundaries, paddle, brick removal, win and loss.

The candidate receives requirements plus `PAT-GAME-0001`, but not `pong/core.py`, `pong/app.py` or Pong tests. This prevents copying from masquerading as transfer.

## A/B design

- Baseline A: fresh agent receives only Breakout requirements.
- Treatment B: fresh agent receives the same requirements plus `PAT-GAME-0001` and `ANTI-GAME-0001`.
- Keep model/version, prompt budget, tools and time budget equal.
- Run at least three paired trials before drawing a directional conclusion.

Primary metrics: first-pass acceptance rate, defects before green, repeated anti-pattern count, time-to-green, architecture violations, security findings and test coverage of required transitions. No competence promotion follows from a single pair.

The executable evaluator in `factory/transfer_eval.py` operationalizes five gate metrics: critical defects, time-to-green minutes, architecture deviations, first-pass acceptance and test completeness. The wider metric set remains diagnostic context.

## Pass rule

`PAT-GAME-0001` remains proposed unless treatment is no worse on critical defects and improves at least two of: first-pass acceptance, time-to-green, test completeness, architecture deviations. An independent Architect and QA must confirm that the functional boundary is real rather than cosmetic.
