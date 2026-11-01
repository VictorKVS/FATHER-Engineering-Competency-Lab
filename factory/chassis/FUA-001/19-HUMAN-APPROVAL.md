# FUA-001 / 19.Human Approval — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 19.01 Purpose
Provide explicit human authorization for privileged or policy-sensitive actions.

## 19.02 Required fields
19.01 Approval Trigger
19.02 Approval Request
19.03 Approver Identity
19.04 Decision
19.05 Timeout
19.06 Escalation
19.07 Approval Evidence

## 19.03 Invariants
- approval is bound to exact action/hash;
- expired approval cannot be replayed;
- approver identity is trusted;
- denial is final for that request version.

## 19.04 Current decision
BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
