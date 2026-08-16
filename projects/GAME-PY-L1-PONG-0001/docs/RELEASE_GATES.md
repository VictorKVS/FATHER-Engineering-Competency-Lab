# Release gates — GAME-PY-L1-PONG-0001

## Passport

- ID/version: `GATE-PY-PONG-0001` / 0.1.0.
- Problem: prevent documentation, code or a mock-up from being presented as a finished game.
- Selected approach: evidence-based milestone gates with explicit blockers.
- Alternatives: subjective readiness; test-count-only readiness; release by calendar date.
- Reason: a gate must combine product, learning, security and packaging evidence.
- Constraint: GUI evidence needs a real display/Windows run and cannot be inferred from headless tests.
- Risk: CI success can be mistaken for playable-product success; the gates keep them separate.
- Links: `EVID-PY-PONG-*`, `TEST-PY-PONG-0001`, `SEC-PY-PONG-0001`, `BUILD-PY-PONG-0001`.

## Gates

| Gate | Product evidence | Learning evidence | Factory evidence | GitHub presentation | Current |
|---|---|---|---|---|---|
| M0 pre-alpha | deterministic core compiles; ≥5 tests | cycle passport and attempt record | proposed pattern | honest README; no fake media | PASS |
| M1 alpha | 12 core tests; CI green 3.11–3.13; Windows GUI smoke | second attempt and defect delta | transfer task specified | CI visible; LICENSE; evidence manifest | PENDING |
| M2 beta | packaged Windows artifact; 30-minute soak; controls checked | independent QA/security reviews | pattern succeeds in second game | real screenshot/GIF and build instructions | BLOCKED |
| RC1 | clean package install/launch; release checklist complete | competence gates evaluated from multiple attempts | golden-pattern decision recorded | signed release notes, checksums and limitations | BLOCKED |

No percentage or document count can override a failed mandatory gate.
