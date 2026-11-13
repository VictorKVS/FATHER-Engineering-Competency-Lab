# FTH-FACTORY-BLOCK-MATERIALIZER-001

Materializes qualified reusable FATHER blocks into an agent/product assembly.

## Status

**QUALIFIED by local Windows run.**

Qualification:
- Ruff: PASS
- chassis regression: **208 passed**
- EMBEDDED_COPY + post-copy SHA-256: PASS
- unqualified block rejection: PASS
- tamper rejection: PASS
- SHARED_SERVICE binding without copy: PASS
- target conflict rejection: PASS

Canonical evidence:
`artifacts/canonical/QUALIFICATION_EVIDENCE.json`

## Delivery modes
- EMBEDDED_COPY
- PACKAGE_DEPENDENCY
- SIDECAR
- SHARED_SERVICE

## Rule

Only QUALIFIED blocks with matching canonical SHA-256 and allowed delivery mode may be assembled.

## End-product rule

A qualified block does not make the assembled agent qualified. The assembled product still requires regression/integration/security qualification.
