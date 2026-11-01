# FUA-001 / 02.Role — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 02.01 Purpose

Define what the agent is allowed and expected to do as a specialist, without embedding provider/model-specific behavior into the role.

## 02.02 Required fields

02.01 Primary Role
02.02 Secondary Roles
02.03 Competence Profile
02.04 Skill Pack
02.05 Allowed Duties
02.06 Forbidden Duties
02.07 Jurisdiction
02.08 Role Tests

## 02.03 Contract

Inputs:
- trusted Identity
- role manifest
- competence/skill registry
- policy profile
- jurisdiction profile

Outputs:
- normalized role profile
- effective duties
- effective restrictions
- required skills
- role evidence reference

Invariants:
- role cannot self-expand beyond policy;
- secondary roles cannot override primary restrictions;
- skill presence does not imply permission;
- role changes are versioned and audited;
- jurisdiction restrictions override role convenience.

## 02.04 Initial threats

T01 role escalation
T02 secondary-role privilege bypass
T03 hidden permission expansion through skill pack
T04 jurisdiction bypass
T05 stale role profile
T06 role/policy divergence
T07 prompt-injected role replacement
T08 conflicting role definitions
T09 unauthorized role mutation
T10 ambiguous duty boundary causing unsafe action

## 02.05 Draft controls

C01 signed/versioned role manifest
C02 deny-by-default duties outside declared scope
C03 policy-engine resolution
C04 conflict detector
C05 jurisdiction guard
C06 role change audit
C07 skill/permission separation
C08 immutable effective-role snapshot per run
C09 approval requirement for privileged role change
C10 role regression suite

## 02.06 Draft test block

### Functional
ROLE-T001 primary role loads
ROLE-T002 secondary roles load without overriding restrictions
ROLE-T003 competence profile resolves
ROLE-T004 skill pack links are explicit
ROLE-T005 allowed/forbidden duties are queryable

### Contract
ROLE-T010 missing primary role rejected
ROLE-T011 conflicting role manifest rejected
ROLE-T012 unknown jurisdiction rejected or quarantined
ROLE-T013 invalid skill reference rejected
ROLE-T014 role version required

### Security
ROLE-T020 prompt cannot redefine effective role
ROLE-T021 model cannot add duty
ROLE-T022 skill pack cannot grant permission
ROLE-T023 secondary role cannot bypass forbidden duty
ROLE-T024 jurisdiction restriction overrides role
ROLE-T025 unauthorized role mutation blocked
ROLE-T026 privileged role change requires approval
ROLE-T027 role/policy divergence blocks sensitive action

### Integration
ROLE-T030 Policy Engine receives effective role
ROLE-T031 Tool Runtime enforces role-derived permissions
ROLE-T032 Planner sees allowed mission scope
ROLE-T033 Audit records role version
ROLE-T034 Evaluator checks role compliance

### Regression
ROLE-T050 model replacement does not alter role semantics
ROLE-T051 prompt-pack replacement does not alter role permissions
ROLE-T052 skill-pack replacement cannot silently expand duties

## 02.07 Acceptance criteria

All mandatory role, policy, jurisdiction and integration tests PASS with evidence.
No unresolved HIGH/CRITICAL privilege or jurisdiction threat.

## 02.08 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
