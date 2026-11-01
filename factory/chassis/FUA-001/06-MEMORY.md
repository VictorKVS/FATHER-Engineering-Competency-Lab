# FUA-001 / 06.Memory — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 06.01 Purpose

Provide bounded, provenance-aware agent memory while separating working context from durable knowledge and preventing memory poisoning.

## 06.02 Required fields

06.01 Working Memory
06.02 Episodic Memory
06.03 Semantic Memory
06.04 Procedural Memory
06.05 User / Project Memory
06.06 Memory Retrieval
06.07 Memory Write Policy
06.08 Memory Retention
06.09 Memory Sanitization
06.10 Memory Poisoning Protection
06.11 Memory Evidence

## 06.03 Contract

Inputs:
- trusted runtime events
- validated user/project facts
- approved knowledge
- tool/RAG observations with provenance
- reflection outputs approved for memory

Outputs:
- memory entries with type, source, confidence, TTL/retention and owner
- retrieval candidates
- write/reject decisions
- memory evidence

Invariants:
- not every context item becomes memory;
- memory write is policy-controlled;
- durable memory stores provenance;
- uncertain inference is never silently promoted to fact;
- user/project memory is isolated by scope;
- deletion/retention policy is enforceable;
- retrieved memory is untrusted input until contextual validation;
- model cannot grant itself durable memory authority.

## 06.04 Initial threats

T01 memory poisoning
T02 false fact promotion
T03 prompt injection persisted as memory
T04 cross-user/project leakage
T05 stale memory dominance
T06 malicious tool/RAG content persisted
T07 unauthorized retention
T08 sensitive data persistence
T09 memory overwrite
T10 confidence inflation
T11 procedural-memory tampering
T12 retrieval bias from poisoned high-rank memory

## 06.05 Draft controls

C01 memory type separation
C02 provenance required
C03 confidence + source support
C04 write-policy gate
C05 quarantine state
C06 scope isolation
C07 retention/TTL
C08 PII/sensitive-data filter
C09 contradiction detector
C10 immutable history for critical edits
C11 approval for privileged/procedural memory
C12 retrieval diversity/recency controls
C13 poison indicators
C14 evidence trail

## 06.06 Draft test block

### Functional
MEM-T001 working memory stores temporary state
MEM-T002 episodic event persists with provenance
MEM-T003 semantic memory stores validated fact
MEM-T004 procedural memory versioned
MEM-T005 retrieval respects scope

### Contract
MEM-T010 memory without source rejected/quarantined
MEM-T011 missing scope rejected
MEM-T012 invalid confidence rejected
MEM-T013 unsupported fact cannot be promoted silently
MEM-T014 retention metadata required where policy demands

### Security
MEM-T020 prompt injection not persisted as trusted memory
MEM-T021 malicious RAG chunk quarantined
MEM-T022 malicious tool output not promoted automatically
MEM-T023 model cannot self-authorize durable write
MEM-T024 cross-project retrieval denied
MEM-T025 sensitive data retention policy enforced
MEM-T026 trust/confidence cannot self-escalate
MEM-T027 procedural memory edit requires stronger approval
MEM-T028 poisoned memory does not override trusted policy/identity
MEM-T029 deletion/retention actions audited

### Quality
MEM-T030 contradiction with trusted memory detected
MEM-T031 stale memory marked/deprioritized
MEM-T032 duplicate memories merged without provenance loss
MEM-T033 inference remains labeled inference
MEM-T034 source revocation propagates to affected memory

### Integration
MEM-T040 Context Manager retrieves bounded set
MEM-T041 Knowledge Runtime distinguishes memory from canonical knowledge
MEM-T042 Policy Engine controls writes
MEM-T043 Evaluator can score memory-supported claims
MEM-T044 Audit records read/write decisions
MEM-T045 Evidence Manager links memory to source

### POLYGON draft
MEM-T060 long-session poisoning attempt
MEM-T061 cross-project leakage attempt
MEM-T062 repeated false claim reinforcement
MEM-T063 conflicting authoritative sources
MEM-T064 malicious document tries to alter agent role through memory
MEM-T065 rollback of compromised memory store
MEM-T066 model replacement with same memory base

## 06.07 Acceptance criteria

Any durable memory without provenance, scope and policy decision is blocking.
Memory poisoning tests are mandatory before installation approval.

## 06.08 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
