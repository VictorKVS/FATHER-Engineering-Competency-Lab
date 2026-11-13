# Business Process
Owner: Senior Business Analyst.

Goal: sensitive actions execute only after explicit human approval where policy requires it.

Actors: agent/factory, human operator, runtime, qualification auditor.

Input: trace_id, action, optional approval_id.
Output: pending ApprovalRecord, approved ApprovalRecord, or execution authorization.

Before: product-level approval could be declared but not reliably enforced/persisted.
After: approval is an executable persistent control.

KPIs:
- protected action without approval blocked: 100%;
- pending survives restart: 100%;
- approved survives restart: 100%;
- wrong/unapproved ID rejected: 100%.

Business rule: reasoning does not equal authority.