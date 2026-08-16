# GAME-PY-L2-BREAKOUT-0002 — baseline task contract

Implement a minimal local Breakout game using Python 3.11+ and only the standard library.

## Product requirements

1. A single player paddle remains inside an 800×600 playfield.
2. A ball bounces from walls and the paddle.
3. The initial level contains at least 3×5 destructible bricks.
4. A valid ball/brick collision removes exactly the intended brick and changes ball direction.
5. Clearing all bricks produces a win state; missing the paddle produces a loss state.
6. Restart restores a playable initial state.
7. Core rules run deterministically without a graphical display.
8. A thin local GUI adapter may use Tkinter; no network, accounts, telemetry, secrets or external assets.

## Acceptance evidence

- Headless tests cover walls, paddle, brick removal, win, loss and restart.
- `python -m unittest discover -s tests -v` passes.
- `python -m compileall -q .` passes.
- README states launch command, controls and known limitations.
- Total non-test Python source is at most 350 physical lines.

## Fixed experiment budget

- Wall-clock budget: 45 minutes.
- Maximum implementation/review iterations: 3.
- Tool scope: local files and Python runtime only.
- Network and external retrieval: disabled.
- Model/provider/version and token usage must be recorded in the result.

Choose and justify the design independently. Do not retrieve or inspect any other FATHER game implementation, pattern, anti-pattern, learning record or review.
