# Control Center LiveLab v0.5 — integration candidate

Status: **LOCAL LAB / NOT QUALIFIED**, built on the v0.4 RBAC overlay and v0.3 Pre-Tester API; no changes to the running chassis yet.

## Changes in runnable lab package
- POST `/api/v1/control/experiments/live`: two sequential real local Ollama `/api/chat` calls (baseline/candidate) with changed model, prompt, temperature.
- `/control` workshop page: model selector, draft, **Real Ollama** experiment action, visible results and trace.
- Local allowlist of Qwen3 8B / Qwen2.5 7B / Qwen2.5-Coder 7B; loopback-only transport.
- Restricted output contract (JSON summary/actions/questions/sources) with source ID validation, duration/tokens/output SHA-256 and audit events.
- Lexical retrieval of 22 existing Tester KB method cards; **not** vector/embedding RAG. `rag_top_k` changes retrieval count, `rag_weight` reserved.
- No generated code execution. Production promotion remains **409 blocked**.
- 52/52 unit/API tests passed in builder environment; model calls mocked in tests. Real Ollama/Windows target hardware **not yet tested**.

## Local package
Archive: `FATHER_Control_Center_LiveLab_v0_5.zip`
SHA-256: `4d9cdf51bb31211229c9a2619cf934427b74cd2ac25fdc2c7437afd1d5c2971c`

Installation: extract as a sibling of existing v0.4 project under `G:\1\FATHER-Engineering-Pipeline\`. The package includes README, API, site, 22 method cards, and tests. This repository page documents the candidate, not an applied `father-chassis` runtime change.

## Integration gates before merge
1. Verify the exact chassis API routes and persistence contracts.
2. Run live Ollama on Windows, check correctness and resource usage.
3. Protect all endpoints with production identity/UAG and persistent audit.
4. Implement independent scoring and qualification before enabling promotion.
5. Obtain human approval with change/provenance evidence.

ADR-005 and full technical documentation are in the local package.
