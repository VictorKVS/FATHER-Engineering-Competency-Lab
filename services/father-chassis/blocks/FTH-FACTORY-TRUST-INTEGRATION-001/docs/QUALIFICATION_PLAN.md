# Qualification Plan
Owner: Qualification Auditor + Test Architect.

Target: G7 M5A TRUST INTEGRATION PACKAGING.

Pass:
- reproducible install;
- Trust public API imports;
- Trust tests PASS;
- chassis tests PASS;
- no sys.path hack;
- cross-package evaluator call works.

Blocking:
missing package, incompatible API, reverse dependency, copied evaluator, hidden path dependency.