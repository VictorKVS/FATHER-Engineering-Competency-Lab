# FUA-001 / 18.Reflection & Learning — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 18.01 Purpose
Improve agent behavior through explicit critique, repair and approved learning artifacts without silently mutating canonical knowledge or policy.

## 18.02 Required fields
18.01 Critic
18.02 Self-Check
18.03 External Verification
18.04 Failure Analysis
18.05 Repair
18.06 Feedback Capture
18.07 Gold Example
18.08 Negative Example
18.09 Skill Improvement
18.10 Learning Gate

## 18.03 Invariants
- reflection output is advisory;
- no self-generated result becomes canonical automatically;
- learning changes require evidence and gate;
- failure history is preserved.

## 18.04 Draft tests
LEARN-T001 critique produces finding
LEARN-T002 repair remains proposed until accepted
LEARN-T003 gold example requires approval
LEARN-T004 negative example retained
LEARN-T020 self-approval forbidden
LEARN-T021 learning cannot modify policy
LEARN-T022 learning cannot canonicalize knowledge
LEARN-T030 feedback provenance preserved

## 18.05 Current decision
BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
