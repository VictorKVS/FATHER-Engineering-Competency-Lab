# FUA-001 Installation / Release Gate v0.1

Purpose:
separate technical readiness from installation authorization.

The gate is fail-closed:
- no human acceptance => DENIED;
- acceptance for a different snapshot => DENIED;
- expired or self-approved acceptance => DENIED;
- any mandatory automated gate not PASS => DENIED;
- only exact snapshot acceptance plus all mandatory gates PASS may produce a PASS decision.

The precheck intentionally keeps:
- installation_permit = DENIED;
- production_ready = false.

This prevents the automated factory from authorizing its own release.
