# FATHER G7 M4 — Typed Stage Artifacts

M4 qualifies versioned typed handoff contracts between engineering roles.

## Acceptance

- qualification toolchain ready;
- compile PASS;
- Ruff F821/F822/F823 PASS;
- full father-chassis regression PASS;
- typed payload serialize/deserialize round-trip PASS;
- nested DevelopmentPacket/Architecture types preserved;
- raw dict stage payload rejected;
- unknown artifact schema version rejected;
- persistent workflow snapshot uses outer schema v2;
- restored workflow contains typed payload instances;
- tampered payload_data still fails artifact hash verification.

## Meaning

M4 proves that JSON is only a persistence representation. Runtime engineering semantics are reconstructed from explicit versioned schemas.

## Not proven

- cross-language schemas;
- automatic v1->v2 legacy snapshot migration;
- distributed schema registry;
- cryptographic schema signatures.
