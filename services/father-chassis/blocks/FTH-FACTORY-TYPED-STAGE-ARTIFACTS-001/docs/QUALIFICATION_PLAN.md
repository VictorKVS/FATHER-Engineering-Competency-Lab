# Qualification Plan
Owner: Qualification Auditor + Test Architect.

Entry:
document pack approved; implementation complete; static checks PASS.

Pass:
- all v1 payload types validate;
- wrong/untyped payloads rejected;
- roundtrip type equality proven;
- nested types preserved;
- persistent workflow restores typed artifacts;
- tamper detection remains effective;
- full regression PASS.

Blocking:
any dict accepted as stage payload; type lost after persistence; schema mismatch accepted; regression failure.

Target qualification:
G7 M4 TYPED STAGE ARTIFACTS.