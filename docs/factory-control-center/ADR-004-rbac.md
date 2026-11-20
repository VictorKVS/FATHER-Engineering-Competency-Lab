# ADR-004: Role- and attribute-based access for FATHER workshops

Status: **PROPOSED FOR FATHER CHASSIS / LAB IMPLEMENTED IN SEPARATE v0.4 OVERLAY**

Decision: all workshop reads and mutations are server-authorized using subject identity, role, allowed stages and projects, action, version, environment, and relevant state. A platform administrator must not automatically obtain a product or examiner's approval authority.

Every edited process graph, prompt, RAG weight or transmitted artifact generates a versioned draft. Production history remains immutable from the agent's perspective; a changed document creates a new branch and downstream re-run. A promotion requires independent evidence and appropriate authorization. In the present demo, promotion is intentionally disabled.

Audit events: ACCESS_DENIED, DRAFT_CREATED, EXPERIMENT_EXECUTED, PROMOTION_BLOCKED. Event payloads include actor, target, requested operation and trace identifiers. The initial SQLite SHA-256 chain is useful for local integrity checks but does not implement WORM or immutable logs.

Security requirements for production: OIDC or mTLS authentication, policy enforcement point for every route, deny by default, scoped service credentials, authorization negative tests, centrally protected audit, no editing exam gold answers, and two-party critical approval.
