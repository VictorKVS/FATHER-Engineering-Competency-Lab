# GAME-PY-L1-PONG-0001 — Pong / Понг

> Status: `0.1.0-pre-alpha`, milestone M1 candidate. The deterministic core is green in CI; the Tkinter UI still requires Windows runtime evidence before alpha.

## RU

Первый эталонный цикл FATHER Game Factory. Ценность проекта — не оригинальность Pong, а прослеживаемый путь от требований и вариантов решения до кода, тестов, доказательств и повторно используемого паттерна.

### Быстрый старт

Требуется Python 3.11+; внешних зависимостей нет.

```bash
cd projects/GAME-PY-L1-PONG-0001
python -m unittest discover -s tests -v
python -m pong.app
```

Управление: `W/S` — левая ракетка, `↑/↓` — правая, `Space` — пауза, `R` — новая партия. Первый игрок до 5 очков побеждает.

## EN

The first reference cycle of FATHER Game Factory. Its value is a traceable path from requirements and alternatives to code, tests, evidence, and reusable factory patterns.

Requirements: Python 3.11+, no third-party dependencies. Run the commands shown above. Controls: `W/S`, arrow keys, `Space` to pause, `R` to restart. First to 5 wins.

## Architecture

```text
keyboard -> Tkinter adapter -> GameState.step(dt) -> immutable rules
                              |                 |
                              +-> renderer      +-> headless unit tests
```

The functional core owns physics and scoring; the UI adapter owns input, time and rendering. This boundary makes the rules testable without a display and limits event/input handling to one module.

## Evidence and limitations

- Automated evidence: deterministic unit tests for symmetric wall/paddle collisions, scoring, clamping, pause/reset, win state and invalid input boundaries.
- CI evidence: 12/12 tests and compilation passed on Python 3.11–3.13 with read-only repository permissions ([run #2](https://github.com/VictorKVS/FATHER-Engineering-Competency-Lab/actions/runs/31923318347)).
- Not yet evidenced: Windows launch, frame pacing, keyboard behavior, visual quality and packaged executable.
- No screenshot/GIF is published until a real build is launched and captured.
- This is not a release candidate. M1 requires manual smoke evidence on Windows plus CI.

## Traceability

- Product/course decision record: [`docs/CYCLE_PASSPORT.md`](docs/CYCLE_PASSPORT.md)
- Learning record: [`learning/attempt-0001.json`](learning/attempt-0001.json)
- Second learning record: [`learning/attempt-0002.json`](learning/attempt-0002.json)
- Release gates: [`docs/RELEASE_GATES.md`](docs/RELEASE_GATES.md)
- Build evidence: [`evidence/EVID-PY-PONG-M1-local.json`](evidence/EVID-PY-PONG-M1-local.json)
- Reusable pattern: [`factory-assets/PAT-GAME-0001-functional-core.md`](factory-assets/PAT-GAME-0001-functional-core.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Changes: [`CHANGELOG.md`](CHANGELOG.md)
