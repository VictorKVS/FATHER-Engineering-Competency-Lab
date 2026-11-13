# Test Contract
Owner: Senior Test Architect.

Acceptance criteria:
AC-AP-01 protected action without approval raises ApprovalRequired.
AC-AP-02 pending record exists.
AC-AP-03 pending survives restart.
AC-AP-04 approve changes status to approved.
AC-AP-05 approved survives second restart.
AC-AP-06 wrong/unapproved ID fails.
AC-AP-07 approval is valid only for matching action.
AC-AP-08 controlled continuation succeeds after approval.
AC-AP-09 protected execution remains auditable.

M2 evidence path:
restart -> restore pending -> approve -> restart -> restore approved -> execute -> qualify.

No qualified hard latency SLO yet.