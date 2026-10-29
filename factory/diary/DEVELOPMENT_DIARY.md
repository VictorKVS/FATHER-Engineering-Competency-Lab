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
