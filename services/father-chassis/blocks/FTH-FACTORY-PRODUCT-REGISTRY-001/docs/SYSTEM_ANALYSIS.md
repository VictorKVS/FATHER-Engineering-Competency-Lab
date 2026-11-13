# System Analysis
Owner: Senior System Analyst.

Requirements:
PR-01 register product/version.
PR-02 identical recipe returns same registration.
PR-03 same product/version with different recipe_hash is rejected.
PR-04 retrieve known registration.
PR-05 list registrations deterministically.
PR-06 persist via StateStore.
PR-07 restore after runtime reopen.

NFR: deterministic identity; fail-closed conflicts; storage-backend abstraction; no father-controller dependency.

State: ABSENT -> ASSEMBLED. CONFLICT is an error outcome.

Errors: unknown product -> KeyError; hash conflict -> ValueError.

Open risks: distributed writers, malformed persisted records, schema migration.