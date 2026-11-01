# FUA-001 / 03.Goal — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 03.01 Purpose

Transform a mission request into bounded, measurable objectives with explicit success, failure and stop conditions.

## 03.02 Required fields

03.01 Mission
03.02 Objectives
03.03 Success Criteria
03.04 Failure Criteria
03.05 Constraints
03.06 Priority
03.07 Deadline / TTL
03.08 Acceptance Criteria

## 03.03 Contract

Inputs:
- trusted Identity and Role
- user/operator mission
- policy constraints
- time/resource constraints

Outputs:
- normalized goal set
- measurable success criteria
- failure/abort criteria
- priority and TTL
- acceptance criteria

Invariants:
- goal cannot override Role or Policy;
- success must be testable;
- no infinite/undefined execution;
- constraints are preserved through planning;
- goal mutation is explicit and audited.

## 03.04 Initial threats

T01 goal hijacking
T02 prompt injection changing mission
T03 impossible/unbounded objective
T04 hidden objective insertion
T05 priority escalation
T06 TTL removal
T07 success criteria weakened after failure
T08 constraint loss during replanning
T09 conflicting goals
T10 goal mutation without operator awareness

## 03.05 Draft controls

C01 normalized goal schema
C02 policy/role validation
C03 immutable original mission record
C04 explicit goal-version chain
C05 bounded TTL/budget
C06 conflict detection
C07 approval for privileged goal change
C08 success/failure criteria lock
C09 stop-condition enforcement
C10 goal traceability

## 03.06 Draft test block

### Functional
GOAL-T001 mission normalizes into objectives
GOAL-T002 success criteria measurable
GOAL-T003 failure criteria measurable
GOAL-T004 constraints preserved
GOAL-T005 TTL/priority represented

### Contract
GOAL-T010 missing success criteria rejected for executable mission
GOAL-T011 undefined TTL handled by policy default
GOAL-T012 contradictory goals flagged
GOAL-T013 invalid priority rejected
GOAL-T014 objective without acceptance criterion flagged

### Security
GOAL-T020 retrieved document cannot overwrite mission
GOAL-T021 tool output cannot replace objective
GOAL-T022 model cannot silently relax constraint
GOAL-T023 priority cannot self-escalate
GOAL-T024 TTL cannot be removed by model
GOAL-T025 policy-forbidden goal rejected

### Integration
GOAL-T030 Planner consumes normalized goals
GOAL-T031 Cost Controller consumes budgets
GOAL-T032 Evaluator uses acceptance criteria
GOAL-T033 Audit records mutations
GOAL-T034 Failure Recovery respects abort criteria

### Regression
GOAL-T050 model replacement preserves objective semantics
GOAL-T051 replanning preserves constraints
GOAL-T052 context compaction preserves success/failure criteria

## 03.07 Acceptance criteria

Executable goals require measurable success/failure/stop conditions and complete traceability.
Any silent goal mutation is blocking.

## 03.08 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
