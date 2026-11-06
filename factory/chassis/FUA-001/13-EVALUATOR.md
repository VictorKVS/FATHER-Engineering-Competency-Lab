# FUA-001 / 13.Evaluator — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 13.01 Purpose

Evaluate task results against explicit acceptance criteria, grounding, policy, cost and regression requirements.

## 13.02 Required fields

13.01 Task Evaluation
13.02 Answer Quality
13.03 Groundedness
13.04 Citation Accuracy
13.05 Hallucination Detection
13.06 Tool Success
13.07 Security Evaluation
13.08 Cost Evaluation
13.09 Latency Evaluation
13.10 Regression Evaluation
13.11 Cross-Model Evaluation

## 13.03 Invariants

- evaluator uses explicit criteria;
- pass requires evidence;
- unknown/not-run is not pass;
- evaluator output cannot self-approve release;
- security failures can override quality pass.

## 13.04 Draft tests

EVAL-T001 evaluate all criteria
EVAL-T002 missing criterion evidence => BLOCKED
EVAL-T003 failed security criterion => FAIL
EVAL-T004 aggregate result deterministic
EVAL-T005 evaluator emits evidence payload
EVAL-T020 model self-score cannot override external test
EVAL-T030 cross-model result comparison
EVAL-T031 regression delta preserved

## 13.05 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
