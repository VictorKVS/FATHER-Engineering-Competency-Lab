# FUA-001 Assembly Runtime — First Integration Draft

Status: ASSEMBLY_TEST_IMPLEMENTED
Version: 0.1

## 32.01 Purpose

Connect the previously isolated FUA blocks into one executable mission path.

## 32.02 Current mission path

03.Goal
→ 04.Planner boundary
→ 08.RAG
→ 17.Context
→ 12.Policy
→ 11.Model Router
→ 10.Tool Runtime
→ 13.Evaluator
→ 14.Audit
→ 15.Observability
→ 21.Resource Controller
→ 22.Evidence
→ 25.Readiness
→ 26.Security

## 32.03 Assembly test principles

- poisoned RAG is excluded from trusted context;
- policy must explicitly allow model/tool actions;
- model selection must satisfy local/privacy/capability constraints;
- resource budget is enforced;
- evaluator requires evidence;
- audit chain must verify;
- evidence artifact is created;
- Readiness remains DENIED until full factory gates are genuinely complete.

## 32.04 Scope limitation

This is the first assembly runtime, not production readiness.
Identity/Role/Goal/Planner/State/Memory/Prompt are not yet all wired into this executable path at full fidelity.
No production model or external tool is used in the assembly test.
