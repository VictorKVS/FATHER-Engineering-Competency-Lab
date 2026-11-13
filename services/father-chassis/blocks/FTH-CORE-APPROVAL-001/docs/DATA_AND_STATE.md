# Data and State
Owner: System Analyst + Data Architect.

Entity: ApprovalRecord.

Persisted fields:
approval_id, trace_id, action, status.

State transition:
PENDING -> APPROVED.

No reverse transition currently exists.
Revocation and expiry are not defined.

Retention: indefinite in current StateStore model.

Consistency invariant:
one approval_id is bound to one action; reuse for another action must fail.

Concurrency:
RLock protects local mutation only. Multi-process coordination pending.