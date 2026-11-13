# Test Contract
Owner: Senior Test Architect.

Acceptance:
AC-TA-01 every defined artifact type accepts its correct payload.
AC-TA-02 wrong payload class is rejected.
AC-TA-03 raw dict payload is rejected at cross-stage boundary.
AC-TA-04 unknown artifact type is rejected.
AC-TA-05 unknown schema version is rejected.
AC-TA-06 serialize -> deserialize preserves typed equality.
AC-TA-07 nested ArchitectureSpec interfaces/variables survive round trip.
AC-TA-08 DevelopmentPacket nested typed objects survive round trip.
AC-TA-09 persisted workflow restores typed payloads.
AC-TA-10 tampered payload still fails artifact hash verification.
AC-TA-11 existing stage-order/role/no-skip tests remain PASS.

Qualification:
full regression + dedicated typed-artifact roundtrip + persistent workflow restart test.