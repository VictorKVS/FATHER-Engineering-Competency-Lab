# BUILD-PY-PONG-0001 — product build passport

- **What:** create an auditable runnable PRODUCT artifact from the tested source.
- **Why:** source plus a roadmap is not a distributable game; the build must be independently checkable.
- **Alternatives:** source-only launch; OS-native executable; Python zip application.
- **Decision:** deterministic `father-pong.pyz` plus SHA-256 manifest. It runs with Python 3.11+ and Tkinter and is explicitly not a standalone executable.
- **Why chosen:** no third-party build dependency, cross-platform format, small attack/dependency surface, and a headless `--self-check` suitable for CI.
- **Constraints:** the target machine must already provide compatible Python and Tkinter.
- **Risks:** Tk availability and real display/input behavior remain environment-specific; zipapp does not prove GUI usability.
- **Evidence:** `scripts/build_zipapp.py`; CI build/self-check/checksum gate; uploaded `father-pong-python-zipapp` workflow artifact.
- **Version:** passport 0.1.0; product 0.1.0-pre-alpha.
- **Links:** `CODE-PY-PONG-0001`, `TEST-PY-PONG-0001`, `SEC-PY-PONG-0001`, `EVID-PY-PONG-M1-LOCAL-0001`.
- **Result:** accept as a pre-alpha Python package; do not promote to alpha or call it an `.exe`.
