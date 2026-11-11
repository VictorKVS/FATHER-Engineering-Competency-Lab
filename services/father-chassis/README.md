# FATHER Chassis / Factory Development

This directory is the canonical GitHub workspace for the reusable FATHER chassis and Factory qualification line.

## Current baseline

- Working baseline: **0.5.0**
- Local regression result: **33/33 tests PASS**
- Qualification:
  - G0 CODE EXISTS — PASS
  - G1 COMPONENT TESTED — PASS
  - G2 INTEGRATED — PASS
  - G3 CHASSIS QUALIFIED — IN PROGRESS
  - G4 PRODUCT QUALIFIED — IN PROGRESS
  - G5 REUSABLE — PASS
  - G6 INDUSTRIAL — NOT STARTED

## Product reuse proof

- OSINT / Knowledge product: 15 shared, 0 adapted, 1 new — reuse ratio 93.75%
- ALINA / BOOKCRAFT product: 15 shared, 3 adapted, 2 new — reuse ratio 75%

## Repository policy

All further FATHER Chassis development is stored here first, with:
1. source code;
2. tests;
3. configuration;
4. qualification reports;
5. BOM / reuse reports;
6. version history.

Runtime databases, secrets, caches and generated local state are not committed.

## Target layout

```
services/father-chassis/
├── src/
├── tests/
├── config/
├── products/
├── artifacts/
├── docs/
└── releases/
```

Development branch: `father-chassis-development`.

The existing `services/father-controller` is intentionally left untouched until integration is qualified.
