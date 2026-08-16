# `PAT-GAME-0001` — Functional core, imperative shell

## Passport

- Version/status: 0.1.0 / proposed, not golden.
- Problem: GUI callbacks mix input, physics and drawing, making behavior difficult to test and reuse.
- Decision: keep game rules in a display-independent state machine; keep clock, keyboard and renderer in a thin adapter.
- Alternatives: callback-owned rules; full ECS; engine framework.
- Why selected: lowest adequate complexity for an L1 project with deterministic tests.
- Constraints: one local scene, simple state, no networking or replay.
- Risks: mutable state can still leak; variable timestep can produce platform differences.
- Evidence: `TEST-PY-PONG-0001`; one project only.
- Related: `ADR-PY-PONG-0001`, `ARCH-PY-PONG-0001`, `ANTI-GAME-0001`, future `XFER-PY-PONG-0001`.

## Promotion rule

Do not call this a golden pattern yet. Promote only after it passes an independent review and a transfer task in a second game (for example Breakout) with equal or lower defect escape and no architecture waiver.

## Anti-pattern

`ANTI-GAME-0001`: assuming discrete overlap collision remains correct for arbitrary speeds or delayed frames. Current mitigation is a capped timestep; higher-speed games must use substeps or continuous collision detection.
