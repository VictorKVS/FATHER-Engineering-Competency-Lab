# FUA-001 Evidence Record — CI FULL ASSEMBLY & SECURITY 0002

Evidence ID: EVID-FUA-CI-0002
Date: 2026-11-01
Branch: factory-v0.1
Status: PASS_WITH_NONBLOCKING_WARNING

## 01. Test evidence

GitHub Actions workflow: FUA-001 API
Run ID: 41298485089
Job ID: 124824309784
Result: SUCCESS

Pytest:
- 89 passed
- 0 failed
- 1 warning
- duration: 0.41 s

Stored artifact:
- name: fua-001-test-evidence
- artifact ID: 13080605784
- format: JUnit XML

The API smoke stage also completed successfully after startup retry.

## 02. Security evidence

GitHub Actions workflow: FUA-001 Security Gates
Run ID: 41298458023
Job ID: 124824222981
Result: SUCCESS

Passed gates:
- SAST / Bandit: PASS
- Dependency audit / pip-audit: PASS
- Secret scan / detect-secrets: PASS
- CycloneDX SBOM generation: PASS
- SBOM upload: PASS

Stored artifact:
- name: fua-001-sbom
- artifact ID: 13079748266

## 03. Assembly evidence

Validated in CI:
- component tests;
- API contract tests;
- negative API tests;
- first assembly runtime;
- full 01-26 assembly runtime;
- POLYGON-LITE adversarial scenarios;
- HTTP endpoint POST /v1/assembly/run;
- OpenAPI contract presence.

## 04. Remaining blockers

This evidence does NOT authorize installation or production.

Still required:
- target workstation full assembly run;
- target workstation live HTTP run;
- target workstation resource evidence;
- real model integration;
- real sandbox isolation;
- compatibility hardening;
- final red-team campaign;
- full POLYGON;
- evidence audit;
- human acceptance.

## 05. Gate decision

CI_COMPONENT_TESTS: PASS
CI_FULL_ASSEMBLY: PASS
CI_API: PASS
CI_SAST: PASS
CI_SCA: PASS
CI_SECRET_SCAN: PASS
CI_SBOM: PASS
POLYGON_LITE: PASS
LOCAL_EVM_FULL_ASSEMBLY: NOT_RUN
INSTALLATION_PERMIT: DENIED
PRODUCTION_READY: NO
