# FUA-001 / 14.Audit — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 14.01 Purpose

Create a tamper-evident trace of user inputs, model/tool/RAG/policy actions and evidence references.

## 14.02 Required fields

14.01 User Input Log
14.02 Prompt Log
14.03 Model Call Log
14.04 RAG Trace
14.05 Tool Call Log
14.06 Policy Decision Log
14.07 Security Event Log
14.08 Evidence Chain
14.09 Tamper Protection
14.10 Retention Policy

## 14.03 Invariants

- every event has sequence, timestamp, actor and correlation id;
- hash chain detects mutation;
- sensitive values are redactable;
- audit is append-only at runtime.

## 14.04 Draft tests

AUD-T001 append event
AUD-T002 sequence monotonic
AUD-T003 hash chain verifies
AUD-T004 modified event breaks verification
AUD-T005 correlation id preserved
AUD-T020 secret redaction
AUD-T030 evidence reference retained

## 14.05 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
