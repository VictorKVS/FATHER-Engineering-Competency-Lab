# FATHER Development Diary

## 2026-10-29 — Bootstrap lessons

### Incident 001 — Local folder was not a Git repository
Observed:
- directory name matched the project name;
- `.git` was absent;
- `git checkout` and `git pull` failed;
- `pyproject.toml` was absent.

Lesson:
Do not infer installation state from folder name.

New factory rule:
Bootstrap must preflight repository identity before issuing update/install commands.

Required checks:
- current directory exists;
- `.git` exists;
- expected remote matches;
- expected branch is active;
- `pyproject.toml` exists;
- runtime package exists.

### Incident 002 — Python version gate was too strict
Observed:
- active interpreter: Python 3.10.11;
- project metadata required Python >=3.11;
- editable install failed before CLI creation.

Root cause:
Declared runtime requirement exceeded actual language features used by the bootstrap code.

Decision:
Lower project minimum to Python >=3.10 because current runtime uses syntax and standard-library features compatible with 3.10.

Lesson:
Runtime compatibility must be derived from real code requirements and target environment, not from a convenient development default.

New factory rule:
Bootstrap preflight must record Python executable, Python version, pip version, platform, repository state and dependency compatibility before installation.

### Effectiveness metric
These incidents show why the factory needs a reproducible bootstrap gate. A future factory should fail early with a precise diagnosis instead of letting the user discover environment assumptions manually.

## 2026-10-29 — Milestone 003: first factory instance generated successfully

Observed on target Windows host:
- repository cloned successfully on branch `feature/father-factory-workshops`;
- editable install completed with Python 3.10.11;
- CLI entry point `father-factory` became available;
- `father-factory --help` exposed `create`, `run-stage`, `inventory-models`;
- `father-factory create --profile OSINT_FACTORY` completed successfully;
- generated instance id: `FATHER-OSINT-FACTORY`;
- generated manifest: `generated_factories/FATHER-OSINT-FACTORY/factory_instance.yaml`;
- generated profile and agent-set configuration were materialized from the reusable blueprint.

### What is now proven

The following chain is no longer conceptual:

BLUEPRINT → PROFILE → CLI → GENERATOR → FACTORY INSTANCE.

This proves the mould can materialize at least one parameterized factory without copying the FATHER core.

### Efficiency lesson

A reusable factory system should minimize manual bootstrap steps and should make environment assumptions explicit before generation.

The next maturity step is to automate preflight and immediately validate the generated instance after creation.

### Next measurable targets

- add `father-factory preflight`;
- run `inventory-models` on the target host;
- validate generated instance contracts;
- execute Stage 000 against the generated factory;
- persist run evidence under the generated instance;
- compare at least two model candidates through the same stage contract.

## 2026-10-29 — Incident 004: model inventory returned empty

Observed:
- `father-factory inventory-models` returned empty Ollama and GGUF lists on the target Windows host.

Interpretation:
This does not prove that no models exist. It proves the first inventory implementation had insufficient discovery coverage.

Root cause:
- Ollama was detected only through PATH;
- GGUF discovery scanned only project-relative or explicitly configured directories;
- LM Studio API and common Windows model locations were not checked.

Decision:
Expand discovery to Ollama API, LM Studio API, common Windows model directories and configurable model roots.

Lesson:
Absence of discovery evidence must not be interpreted as evidence of absence.

New canon:
Inventory systems must report what was scanned, what was reachable and why an asset may be missing.


## 2026-10-29 — Milestone 005: physical Model Zoo discovered

Target-host inventory successfully discovered local assets.

Observed runtime state:
- Ollama CLI reachable;
- Ollama API reachable;
- Ollama currently reports no registered models;
- LM Studio API is not running;
- GGUF files are present under the LM Studio model store;
- OLLAMA_MODELS points to F:/FATHER_MODELS/ollama.

Discovered capability classes:
- general/reasoning LLMs: local GigaChat variants, Qwen2.5 14B;
- coding LLMs: Qwen2.5-Coder 14B, DeepSeek-Coder-V2-Lite Q4/Q5;
- multimodal: LLaVA variants, CogVLM;
- embeddings: BGE-M3;
- speech-to-text: Whisper Large V3 Turbo;
- multimodal projector files: mmproj files, which must not be treated as standalone models.

Key lesson:
The machine already contained a substantially richer model zoo than our prior registry indicated. New downloads should therefore be driven by capability/eval gaps, not assumptions.

Next experiment:
Create a normalized Model Zoo manifest and run same-contract A/B/N tests for ALINA and FATHER_CODEX.


## 2026-10-29 — Incident 006: HTTP alive before model ready

Observed:
- llama-server executable started successfully;
- server accepted HTTP requests on 127.0.0.1:8080;
- `/v1/models` returned HTTP 503 with message `Loading model`;
- llama-server warned that CORS allowed all origins and no API key was set.

Interpretation:
HTTP availability and model readiness are different states.

New runtime state model:
SERVER_DOWN → STARTING → READY → INFERENCE_ACTIVE → DEGRADED/FAILED.

Security lesson:
Even localhost AI runtimes need an explicit browser-origin policy. Default CORS=* is not acceptable as the FATHER baseline.

Decision:
- same-machine baseline uses `--cors-origins localhost`;
- API authentication is supported via runtime secret, not repository config;
- 503 Loading model is treated as STARTING, not a failed model.

Efficiency lesson:
Preflight must distinguish process presence, HTTP readiness, model readiness and inference readiness rather than reporting one boolean.
