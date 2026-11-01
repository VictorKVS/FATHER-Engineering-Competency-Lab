# FUA-001 / 04.Task Planner — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 04.01 Purpose

Convert validated goals into a bounded, policy-compliant, evidence-producing execution plan.

## 04.02 Required fields

04.01 Task Decomposition
04.02 Dependency Graph
04.03 Priority Queue
04.04 Resource Planning
04.05 Risk Planning
04.06 Tool Planning
04.07 Model Planning
04.08 Retry Strategy
04.09 Abort Strategy
04.10 Plan Evidence

## 04.03 Contract

Inputs:
- trusted Identity
- effective Role
- validated Goals
- current State
- available Models
- available Tools
- policies
- budgets

Outputs:
- task graph
- dependencies
- execution order
- model/tool selections as proposals
- retry/abort conditions
- plan evidence

Invariants:
- planner proposes; Policy Engine authorizes;
- every privileged tool step is explicit;
- every task maps to a goal;
- every dependency is represented;
- budget and stop conditions remain binding;
- plan mutations are versioned.

## 04.04 Initial threats

T01 hidden subtask
T02 unsafe tool planning
T03 privilege escalation through task decomposition
T04 infinite planning loop
T05 recursive task explosion
T06 ignored dependencies
T07 budget evasion
T08 selecting unapproved model/tool
T09 risky parallelization
T10 plan injection from untrusted RAG/tool output
T11 retry storm
T12 abort suppression

## 04.05 Draft controls

C01 typed task graph
C02 max task depth/width
C03 policy pre-check for each action class
C04 explicit tool/model IDs
C05 resource budget binding
C06 retry cap/backoff
C07 abort criteria
C08 risk annotation
C09 provenance for plan inputs
C10 immutable plan versions
C11 dependency validation
C12 human approval hooks

## 04.06 Draft test block

### Functional
PLAN-T001 simple goal decomposes correctly
PLAN-T002 multi-step dependencies preserved
PLAN-T003 priority ordering deterministic under same inputs
PLAN-T004 resource estimates emitted
PLAN-T005 retry and abort strategies emitted

### Contract
PLAN-T010 orphan task rejected
PLAN-T011 cyclic dependency detected
PLAN-T012 task without goal link rejected
PLAN-T013 invalid tool/model reference rejected
PLAN-T014 missing stop condition rejected for iterative plan

### Security
PLAN-T020 untrusted RAG text cannot inject hidden task
PLAN-T021 tool output cannot authorize next privileged action
PLAN-T022 planner cannot bypass Policy Engine
PLAN-T023 forbidden tool plan blocked
PLAN-T024 recursive task explosion bounded
PLAN-T025 retry storm bounded
PLAN-T026 budget bypass rejected
PLAN-T027 privileged parallel tasks require policy approval
PLAN-T028 plan mutation audited

### Reliability
PLAN-T030 model timeout triggers bounded fallback/retry
PLAN-T031 partial-plan recovery from checkpoint
PLAN-T032 invalid planner output fails safely
PLAN-T033 unavailable tool causes replan or safe stop

### Integration
PLAN-T040 Goal traceability maintained
PLAN-T041 State receives plan checkpoint
PLAN-T042 Model Router receives task requirements
PLAN-T043 Tool Runtime receives explicit tool requests only
PLAN-T044 Audit records plan version
PLAN-T045 Evaluator can compare executed vs planned steps

### POLYGON draft
PLAN-T060 long-horizon 20-step mission
PLAN-T061 conflicting constraints mission
PLAN-T062 adversarial retrieved instruction
PLAN-T063 model swap mid-plan
PLAN-T064 tool failure mid-plan
PLAN-T065 cost budget exhaustion
PLAN-T066 human approval interruption/resume

## 04.07 Acceptance criteria

No executable plan may contain an orphan, unauthorized, unbounded or unaudited action.
Long-horizon and adversarial POLYGON cases are mandatory before installation approval.

## 04.08 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
