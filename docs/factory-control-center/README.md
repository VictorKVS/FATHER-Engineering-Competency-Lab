# FATHER Factory Control Center — RBAC integration (v0.4 laboratory)

**Status:** Experimental laboratory overlay to the existing FATHER Pre-Tester API v0.3. Not qualified for production. The runnable local package is distributed separately as `FATHER_Control_Center_RBAC_v0_4.zip`.

## Control Center
The factory graph has stage passports, handoff arrows, status, and drill-down. Clicking a workshop opens its current configuration, permitted document operations, last runs, the trial editor, tests and audit history.

Stage controls:
- `observer`: read-only
- `operator`: run training scenarios
- `specialist`: create drafts/experiments for assigned stages
- `lead`: approve changes within own scope after independent evidence (future)
- `architect`: design handoff topology (future)
- `platform_admin`: infrastructure, no permission to rewrite professional results
- `factory_owner`: critical approvals under policy (future)

Do not implement rank-based automatic privileges. Authorize `subject + action + resource + stage + project + environment + version` server-side. Never rely solely on hidden UI controls.

## Endpoints in the local v0.4 overlay
- `GET /api/v1/access/me`
- `GET /api/v1/control/map`
- `GET /api/v1/control/stages/{id}/configuration`
- `POST /api/v1/control/stages/{id}/drafts`
- `GET /api/v1/control/drafts/{id}`
- `POST /api/v1/control/experiments`
- `GET /api/v1/control/experiments/{id}`
- `GET /api/v1/control/audit`
- `POST /api/v1/control/configurations/{id}/promote` => **409**: promotion not allowed in simulator.

## Evidence and limits
The local overlay passed **39/39 automated unit/API tests** on 2026-11-20 (19 existing + 20 new). It keeps the 7-stage simulated process and synthetic pre-Tester documents; experiments do **not** actually run changed LLM/RAG settings. The reported experiment result is `SIMULATED_STRUCTURAL_ONLY` and `NOT_QUALIFIED`.

The local token prototype is NOT production IAM. Do not expose on the internet or merge into a production service without proper identity, UAG enforcement on all operations, persistent protected audit, approvals, and security review.

## Integration path
1. Keep the current `father-chassis` runtime unchanged until parity tests pass.
2. Adopt this access policy and control-center route specification.
3. Connect an authenticated FATHER chassis API adapter and actual agent configurations.
4. Re-run independent contract, regression, negative-authority and UAG tests.
5. Require evidence and human approval before promotion.

Source training API package SHA-256:
`34e458c906f9a9b8d7277a18fab31da6d9f377d540dc06a53f0d529f1f41fc7e`
