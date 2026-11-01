# FUA-001 / 17.Context Manager — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 17.01 Purpose

Build bounded model context while preserving mandatory policy/identity instructions and source labels.

## 17.02 Required fields

17.01 Context Budget
17.02 Context Selection
17.03 Compression
17.04 Summarization
17.05 Priority
17.06 Sensitive Data Removal
17.07 Context Overflow Recovery
17.08 Context Evidence

## 17.03 Invariants

- mandatory security context cannot be evicted by ordinary content;
- each segment has trust/source metadata;
- budget overflow is explicit;
- sensitive content filtering precedes remote model use.

## 17.04 Draft tests

CTX-T001 respect token/character budget
CTX-T002 mandatory segment retained
CTX-T003 low-priority segment dropped first
CTX-T004 source metadata preserved
CTX-T020 sensitive segment removed for remote target
CTX-T021 injection text not promoted to instruction

## 17.05 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
