# FUA-001 API Design v0.1

## 00. API mission

Expose FUA as a controlled engineering product while preserving block boundaries.

## 01. API architecture rules

01.01 API is not a privileged bypass.
01.02 Every write request is attributable to trusted identity.
01.03 Authorization is resolved from Identity + Role + Policy.
01.04 Idempotency is mandatory for mission creation.
01.05 Sensitive state mutations require audit and evidence.
01.06 Durable memory POST means REQUEST WRITE, not unconditional write.
01.07 Prompt assembly returns metadata/hash; sensitive assembled prompts may be withheld by policy.
01.08 Runtime identity fields are server-authoritative.
01.09 Installation Permit and readiness are read from certification evidence.
01.10 RFC 9457-style problem responses are used for contract/policy errors.

## 02. Endpoint map

- 00.Control: GET /health
- 01.Identity: POST /v1/agents
- 01.Identity: GET /v1/agents/{agent_id}
- 01.Identity: POST /v1/agents/{agent_id}/instances
- 02.Role: GET /v1/agents/{agent_id}/role
- 03.Goal + 04.Planner: POST /v1/agents/{agent_id}/missions
- 04.Planner: GET /v1/agents/{agent_id}/plans/{plan_id}
- 05.State: GET /v1/agents/{agent_id}/state
- 05.State: POST /v1/agents/{agent_id}/checkpoints
- 06.Memory: POST /v1/agents/{agent_id}/memory/query
- 06.Memory: POST /v1/agents/{agent_id}/memory
- 07.Prompt: POST /v1/agents/{agent_id}/prompts/assemble
- 25.Readiness: GET /v1/agents/{agent_id}/readiness

## 03. Security baseline

- TLS outside loopback development.
- Bearer/OIDC adapter at ingress; exact provider remains replaceable.
- deny-by-default authorization.
- request size limits.
- schema validation with additionalProperties=false on critical contracts.
- server-side trusted Agent/Instance identity.
- idempotency and replay defense for mutation endpoints.
- rate limits by identity/role.
- trace_id on every request.
- audit event on every privileged decision.
- no secrets returned in diagnostics.
- content from RAG/tools/memory treated as untrusted data.

## 04. DevSecOps gates for API

Before INSTALLATION_APPROVED:
- OpenAPI schema validation;
- contract tests generated from spec;
- negative schema tests;
- authn/authz tests;
- BOLA/IDOR tests;
- replay/idempotency tests;
- rate-limit tests;
- injection payload tests;
- secret leakage tests;
- dependency/SBOM/SCA;
- SAST;
- API fuzzing;
- observability/audit correlation tests;
- POLYGON mission tests.

## 05. API status

DESIGN_DEFINED.
IMPLEMENTATION_NOT_YET_APPROVED.
INSTALLATION_PERMIT: DENIED.
