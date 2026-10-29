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
