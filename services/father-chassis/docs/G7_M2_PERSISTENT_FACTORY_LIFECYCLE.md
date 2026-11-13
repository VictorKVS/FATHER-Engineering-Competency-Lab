# FATHER G7 M2 — Persistent Factory Lifecycle

M2 proves that factory identity and human approval decisions survive runtime restart.

## Lifecycle under test

```text
compose product
  -> register product
  -> request human approval
  -> restart runtime
  -> restore product registry
  -> restore pending approval
  -> approve
  -> restart runtime
  -> restore approved decision
  -> execute product
  -> qualify
```

## Acceptance

- full father-chassis regression PASS;
- product registration survives restart;
- pending approval survives restart;
- approved decision survives another restart;
- post-restart product execution succeeds;
- product remains tied to the same recipe and assembly hashes;
- resulting execution is qualified.

M2 does not yet prove multi-node concurrent writes, approval expiration/revocation, external signatures, or per-product Docker deployment.
