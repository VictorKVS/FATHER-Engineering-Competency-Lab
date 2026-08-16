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
python scripts/build_zipapp.py
python dist/father-pong.pyz --self-check
python -m factory.experiment_packet compare experiments/EXP-BREAKOUT-A1 experiments/EXP-BREAKOUT-B1
python -m factory.experiment_packet build experiments/EXP-BREAKOUT-A1 dist/EXP-BREAKOUT-A1.zip
python -m factory.experiment_packet build experiments/EXP-BREAKOUT-B1 dist/EXP-BREAKOUT-B1.zip
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
- Windows hosted CI verifies compilation, 12 core tests, Tkinter/application import and smoke-script syntax ([run #4](https://github.com/VictorKVS/FATHER-Engineering-Competency-Lab/actions/runs/31930397152)). It does not replace the real-window checklist.
- The PRODUCT pipeline builds a deterministic Python zipapp, executes its headless self-check and verifies its SHA-256 manifest. This is not a standalone executable and still requires Python/Tkinter.
- Packaging evidence: 16/16 tests across Linux 3.11–3.13 and Windows 3.12, plus build/self-check/checksum/upload, passed in [run #6](https://github.com/VictorKVS/FATHER-Engineering-Competency-Lab/actions/runs/31938141556).
- Not yet evidenced: Windows launch, frame pacing, keyboard behavior, visual quality and standalone executable.
- No screenshot/GIF is published until a real build is launched and captured.
- This is not a release candidate. M1 requires manual smoke evidence on Windows plus CI.

## Traceability

- Product/course decision record: [`docs/CYCLE_PASSPORT.md`](docs/CYCLE_PASSPORT.md)
- Learning record: [`learning/attempt-0001.json`](learning/attempt-0001.json)
- Second learning record: [`learning/attempt-0002.json`](learning/attempt-0002.json)
- Release gates: [`docs/RELEASE_GATES.md`](docs/RELEASE_GATES.md)
- Build evidence: [`evidence/EVID-PY-PONG-M1-local.json`](evidence/EVID-PY-PONG-M1-local.json)
- Windows GUI procedure: [`docs/WINDOWS_SMOKE_PASSPORT.md`](docs/WINDOWS_SMOKE_PASSPORT.md)
- Product build passport: [`docs/BUILD_PASSPORT.md`](docs/BUILD_PASSPORT.md)
- Pre-alpha release notes: [`docs/RELEASE_NOTES_0.1.0-pre-alpha.md`](docs/RELEASE_NOTES_0.1.0-pre-alpha.md)
- Transfer experiment: [`factory-assets/XFER-PY-PONG-0001-breakout.md`](factory-assets/XFER-PY-PONG-0001-breakout.md)
- L1–L10 benchmark and three-level gates: [`docs/BENCHMARK_PASSPORT.md`](docs/BENCHMARK_PASSPORT.md)
- Machine-readable benchmark catalog: [`benchmarks/BENCHMARK-10-GAME-PROGRAMMER.json`](benchmarks/BENCHMARK-10-GAME-PROGRAMMER.json)
- Sealed Breakout baseline: [`docs/EXPERIMENT_BREAKOUT_A1_PASSPORT.md`](docs/EXPERIMENT_BREAKOUT_A1_PASSPORT.md)
- Sealed Breakout treatment: [`docs/EXPERIMENT_BREAKOUT_B1_PASSPORT.md`](docs/EXPERIMENT_BREAKOUT_B1_PASSPORT.md)
- Reusable pattern: [`factory-assets/PAT-GAME-0001-functional-core.md`](factory-assets/PAT-GAME-0001-functional-core.md)
- Reusable anti-pattern: [`factory-assets/ANTI-GAME-0001-discrete-collision.md`](factory-assets/ANTI-GAME-0001-discrete-collision.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Changes: [`CHANGELOG.md`](CHANGELOG.md)
