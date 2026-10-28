# FATHER Factory — Build and Test Order

## Rule

Сначала проверяется фабрика как производственная система.
Только после прохождения фабричных gate начинается квалификация отдельных агентов.

Нельзя считать агента провалившим тест, если причиной является неисправность фабричного runtime, API handoff, state machine, artifact storage или UI.

---

## PHASE F0 — Factory Skeleton

Required:
- Product Field
- Product Dossier
- Agent Registry
- Specialist Registry
- standard agent package
- standard API handoff envelope
- state/status model
- gate model
- artifact/evidence model
- event model
- specialist workspace
- versioning/provenance rules

Exit:
FACTORY_SKELETON_READY

---

## PHASE F1 — Agent Runtime Contract

Required:
- load agent profile
- load ROLE / PROMPT / ALGORITHM
- load RAG manifest
- resolve KB refs
- validate input contract
- execute via temporary LLM runtime
- validate output contract
- run checklist/evals
- save evidence
- create handoff
- update product state

Exit:
AGENT_RUNTIME_CONTRACT_READY

---

## PHASE F2 — Factory Handoff Tests

Test:
A → B payload
schema/version
accept/reject
HOLD
rework
resubmit
evidence
correlation/run IDs
failed validation
version conflict
security block

Exit:
HANDOFF_ENGINE_VERIFIED

---

## PHASE F3 — Product Lifecycle Tests

Run synthetic product through:
IDEA
→ PRODUCT MANAGER
→ ALINA
→ OSINT
→ ALINA
→ PIONEER
→ SECURITY
→ CODEX
→ TEST
→ TIMA
→ QA/EVALS
→ OPTIMIZATION
→ RC
→ POLYGON
→ RELEASE

At this phase specialist intelligence may use deterministic fixtures.
We test factory mechanics, not specialist quality.

Exit:
FACTORY_E2E_VERIFIED

---

## PHASE F4 — Failure / Rework Tests

Mandatory:
- specialist HOLD
- specialist FAIL
- missing artifact
- invalid schema
- incomplete evidence
- wrong version
- unavailable tool
- research gap
- architecture gap
- failed test
- Polygon FAIL
- rollback/rework path

Exit:
FACTORY_REWORK_VERIFIED

---

## PHASE F5 — UI / Evidence Tests

Verify:
- product status color
- current specialist
- gate
- documents
- tests
- evidence
- history
- specialist drilldown
- handoff visibility
- failure/rework visibility

Exit:
FACTORY_UI_EVIDENCE_VERIFIED

---

# AFTER FACTORY PASS — AGENT QUALIFICATION

## A1 — AG-000 Product Manager
Run 3 packs.

## A2 — AG-001 ALINA
Run 3 individual packs.

## A3 — AG-010 OSINT
Run 3 individual packs.

## A4 — AG-005 PIONEER
Run 3 individual packs.

## A5 — ALINA + OSINT + PIONEER Workcell
Run 3 cross-agent E2E packs.

Then:
Security
→ FATHER_CODEX
→ Test Engineer
→ TIMA
→ QA/Evals
→ Optimization
→ Polygon.

---

## Promotion rule

FACTORY PASS
does not mean
AGENT PASS.

AGENT PASS
does not mean
PRODUCT PASS.

Each layer has its own evidence and gate.
