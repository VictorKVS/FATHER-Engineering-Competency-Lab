# System Analysis
Owner: Senior System Analyst.

Requirements:
AP-01 create pending approval.
AP-02 persist pending approval.
AP-03 restore pending approval.
AP-04 approve existing request.
AP-05 persist approved state.
AP-06 restore approved state.
AP-07 validate exact action binding.
AP-08 reject invalid/unapproved IDs.
AP-09 raise ApprovalRequired when protected action lacks approval.

NFR: fail-closed; process-local thread safety; StateStore abstraction; auditability.

States: PENDING -> APPROVED.

Errors:
unknown ID -> KeyError;
invalid/unapproved ID -> PermissionError;
missing required approval -> ApprovalRequired.

Open requirements: TTL, revocation, approver identity, multi-party approval.