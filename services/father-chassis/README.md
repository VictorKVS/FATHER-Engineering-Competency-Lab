# FATHER Chassis / Factory Development

> Русская версия: [README_RU.md](README_RU.md)

## Current version: 0.8.0

**Regression: 44/44 tests PASS.**

FATHER Chassis is the reusable runtime and factory foundation for multiple AI/agent products.

### 0.8 highlights

- OpenAI-compatible local LLM profile;
- `/models/local/probe` model discovery/health probe;
- `/qualification/knowledge` end-to-end qualification endpoint;
- Windows PowerShell real-LLM qualification script;
- document → RAG → evidence → LLM → audit qualification path;
- full RU/EN qualification runbooks.

## Qualification status

```text
G0 CODE EXISTS             PASS
G1 COMPONENT TESTED        PASS
G2 INTEGRATED              PASS
G3 CHASSIS QUALIFIED       PENDING WINDOWS + REAL LLM
G4 PRODUCT QUALIFIED       IN PROGRESS
G5 REUSABLE                PASS
G6 INDUSTRIAL              NOT STARTED
```

G3 is intentionally not marked PASS until the target Windows workstation validates Docker, PostgreSQL/pgvector, Redis and a real local LLM.

See [RUNBOOK_0_8_EN.md](docs/RUNBOOK_0_8_EN.md).
