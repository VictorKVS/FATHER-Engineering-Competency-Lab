# Cycle passport — GAME-PY-L1-PONG-0001 / M0

| Field | Value |
|---|---|
| Passport ID | `PASS-GAME-PY-PONG-0001-M0` |
| Version | 0.1.0 |
| Status | accepted for pre-alpha; not RC |
| Decision date | 2026-08-16 |
| Owner roles | Analyst, Architect, Security Engineer, QA, Programmer |
| Links | `REQ-PY-PONG-0001`, `ADR-PY-PONG-0001`, `ARCH-PY-PONG-0001`, `SEC-PY-PONG-0001`, `TEST-PY-PONG-0001`, `CODE-PY-PONG-0001`, `PAT-GAME-0001` |

## Source, idea and analyst brief

Create a deliberately small Pong clone as the first fully traceable factory exercise. The product goal is a two-player local game to five points. The research goal is to prove a repeatable engineering cycle with evidence. This is an original exercise based on the public-domain game concept; no book text or third-party code is copied.

## Requirements (`REQ-PY-PONG-0001`)

1. Two independently controlled paddles remain inside an 800×450 field.
2. The ball bounces from top/bottom walls and paddles.
3. A missed ball increments the opponent score and resets play.
4. First to five wins; restart and pause are available.
5. Core rules run and test without a graphical display.
6. No network, account, telemetry, file write or secret is required.

Acceptance gate M0: requirements 1–5 have automated core evidence; documentation explicitly distinguishes automated and manual evidence.

## Alternatives and decision (`ADR-PY-PONG-0001`)

| Alternative | Benefit | Cost/risk | Decision |
|---|---|---|---|
| Pygame | Familiar game API | external dependency and install friction | defer |
| Tkinter with logic in callbacks | shortest demo | tightly coupled and hard to test | reject |
| Tkinter adapter + pure Python core | standard library, headless tests, clear boundary | slightly more structure | choose |
| Terminal Pong | easiest headless execution | weak input/rendering lesson | reject for product; retain as fallback idea |

Decision: separate deterministic rules from time/input/render adapters. Revisit if later lessons require audio, sprites or packaging that justify Pygame.

## Architecture (`ARCH-PY-PONG-0001`)

`GameConfig` declares invariants; `GameState` owns transitions; `PongApp` translates keyboard/time and renders state. The core has no Tkinter import. The 50 ms timestep cap reduces collision tunnelling after a stalled window. Constraint: collision response is intentionally simple and has no spin or continuous collision detection.

## Security review (`SEC-PY-PONG-0001`)

Attack surface is small: local keyboard and GUI event loop only. No untrusted file parsing, deserialization, network, shell, secrets or personal data. Controls: bounded timestep, bounded paddle position, fixed controls, no dynamic evaluation. Residual risks: event flooding can degrade responsiveness; future save/mod/network features require new threat modelling. Security gate passes for local pre-alpha only.

## QA and evidence (`TEST-PY-PONG-0001`)

Automated tests cover boundary clamp, wall collision, paddle collision, score/reset and match termination. Missing evidence: bottom/right symmetric paths, pause behavior, Windows GUI smoke, long-run stability, accessibility and executable packaging. These omissions block RC1, not M0.

Initial execution found `DEF-PY-PONG-0001`: the winning-score test placed the ball outside the field but did not set its travel direction, so the arrange phase was internally inconsistent. `FIX-PY-PONG-0001` makes position and velocity explicit. `LESSON-PY-PONG-0001`: physics tests must control the complete relevant state, not rely on constructor defaults. The defect did not escape the development gate.

## Implementation/review decision

`CODE-PY-PONG-0001` implements the chosen boundary with only the standard library. Review finding `REV-PY-PONG-0001`: the minimal collision model can tunnel at extreme velocities; mitigation is timestep capping, with continuous collision detection deferred and recorded as `ANTI-GAME-0001` if future code silently assumes arbitrary velocities are safe.

## Result, risks and next gate

M0 decision: accept as pre-alpha after automated tests pass. M1 requires CI on Python 3.11–3.13, manual Windows launch record, symmetric test expansion and a build/evidence manifest. Only after those pass may version `0.2.0-alpha` be considered. RC1 additionally requires packaged-product smoke evidence, license audit and release notes.
