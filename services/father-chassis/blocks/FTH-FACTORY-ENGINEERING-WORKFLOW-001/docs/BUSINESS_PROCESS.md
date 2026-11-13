# Business Process
Owner: Senior Business Analyst.

Goal: engineering work must continue after restart without losing which stages passed, which artifacts were approved, or which role is allowed to work next.

Input: approved customer request and subsequent approved stage artifacts.
Output: deterministic next-stage authority and complete workflow history.

KPIs:
- stage order preserved after restart: 100%;
- approved artifacts restored: 100%;
- skipped stages blocked: 100%;
- artifact hash tampering detected: 100%.

Business rule:
restart must not reset engineering governance.