# FATHER Brain & Knowledge Infrastructure
## 04 — Test Architecture

**Stage:** Test Architecture  
**Scope:** FTH-BRAIN-SUPPLY-001  
**Decision:** TEST ARCH PASS for reference v1; development authorized.

## 1. Test objective

Prove that Brain Supply Resolver supplies only an explicitly compatible, authorized and qualified Brain Package, remains deterministic, and fails closed under mismatch or ambiguity.

## 2. Test layers

### Unit
Pure Python rule and identity tests.

### Regression
Full `father-chassis` pytest suite.

### Qualification harness
Windows PowerShell harness runs:
1. Ruff;
2. full pytest regression;
3. controlled supply scenarios;
4. evidence JSON generation.

## 3. Mandatory positive case

A package binds only when:
- requested Brain Class matches;
- agent class is compatible;
- role is allowed;
- domain is covered;
- capabilities are covered;
- supply mode is supported;
- classification is authorized;
- tenant is compatible;
- package lifecycle is eligible.

## 4. Mandatory negative cases

- wrong brain class;
- missing capability;
- wrong domain;
- wrong role;
- unsupported supply mode;
- unauthorized classification;
- cross-tenant access;
- DRAFT/unqualified state;
- REVOKED state;
- implicit higher-class substitution;
- invalid policy/request;
- ambiguous candidates.

## 5. Determinism

The same request, package set and policy must produce the same decision identity regardless of candidate input order.

Policy version change must change decision identity.

## 6. Security assertions

A denial must not leak storage credentials or perform storage access.
The resolver is authorization pre-binding, not retrieval execution.
No probabilistic recommendation may override a denial.

## 7. Evidence

Qualification evidence must include booleans for all mandatory invariants plus:
- decision_id;
- selected_package_id for positive scenario;
- policy_id/version;
- completed_at_utc;
- regression status.

## 8. Gate

Development may begin because:
- test target is bounded;
- PASS/FAIL semantics are explicit;
- security-negative cases are mandatory;
- local Windows qualification remains required before promotion.
