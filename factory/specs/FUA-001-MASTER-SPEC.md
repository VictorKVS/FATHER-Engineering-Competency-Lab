# FUA-001 — FATHER Universal Agent Master Specification

Status: APPROVED PLAN / IMPLEMENTATION STARTED
Version: 0.1
Date: 2026-11-01

## 00. FATHER Engineering Law

No component is READY until its operation is proven inside the final assembled product.

A component exists as an engineering artifact only when all required elements exist:

REQUIREMENT
+ CONTRACT
+ IMPLEMENTATION
+ THREAT MODEL
+ TEST BLOCK
+ SECURITY TESTS
+ INTEGRATION TESTS
+ OBSERVABILITY
+ EVIDENCE
+ PROVENANCE

Absence of a required element blocks PRODUCTION_READY.

## 01. FUA CORE

01. Identity
02. Role
03. Goal
04. Task Planner
05. State
06. Memory
07. Prompt Runtime
08. RAG Runtime
09. Knowledge Runtime
10. Tool Runtime
11. Model Router
12. Policy Engine
13. Evaluator
14. Audit
15. Observability

## 02. Extended Chassis

16. Skill Runtime
17. Context Manager
18. Reflection / Learning
19. Human Approval
20. Execution Sandbox
21. Cost / Resource Controller
22. Evidence Manager
23. Compatibility Manager
24. Failure Recovery
25. Release / Readiness Gate
26. Security Operating Layer

## 03. Mandatory block lifecycle

00. DRAFT
01. REQUIREMENTS_DEFINED
02. CONTRACT_DEFINED
03. TESTS_DRAFTED
04. THREAT_MODELED
05. IMPLEMENTED
06. STATIC_VALIDATED
07. UNIT_TESTED
08. SECURITY_TESTED
09. COMPATIBILITY_TESTED
10. INTEGRATION_TESTED
11. RED_TEAM_TESTED
12. POLYGON_TESTED
13. EVIDENCE_AUDITED
14. INSTALLATION_APPROVED
15. ASSEMBLED
16. PRODUCT_TESTED
17. PRODUCTION_READY

Rules:
- IMPLEMENTED != READY
- TESTED != PRODUCTION_READY
- CI GREEN != SECURITY_VALIDATED
- RUNTIME_WORKS != PRODUCT_WORKS
- NOT_TESTED != PASS
- NOT_TESTED = BLOCKED
- NO_EVIDENCE = NO_PASS

## 04. Mandatory block passport

Every block must contain:

01. ID
02. Version
03. Purpose
04. Inputs
05. Outputs
06. Contract
07. Dependencies
08. Configuration
09. Permissions
10. Data Classification
11. Threats
12. Security Controls
13. Failure Modes
14. Logging
15. Metrics
16. Tests
17. Security Tests
18. Compatibility Tests
19. Evidence
20. Provenance
21. SBOM
22. Vulnerability Status
23. Owner
24. Lifecycle Status
25. Release Status

## 05. FATHER Four Eyes Rule

Author of block != author of tests != security examiner != final approver.

Development automation may draft all artifacts, but release approval requires independent validation roles.

## 06. Test-before-install rule

Every block receives a TEST BLOCK before implementation is accepted.

No block can be included in an assembly manifest unless:

INSTALLATION_PERMIT = PASS

## 07. Three proof levels

07.01 COMPONENT TEST
Prove block behavior in isolation.

07.02 ASSEMBLY TEST
Prove behavior with dependent and adjacent blocks.

07.03 PRODUCT TEST
Prove the complete specialized FUA solves real product tasks.

## 08. Threat-to-evidence chain

THREAT
→ CONTROL
→ TEST
→ EVIDENCE
→ RESIDUAL RISK
→ DECISION

## 09. Test inheritance

A product test set is composed from:

FATHER_GLOBAL_TESTS
+ FUA_GLOBAL_TESTS
+ BLOCK_TYPE_TESTS
+ SECURITY_TESTS
+ CHASSIS_TESTS
+ DOMAIN_TESTS
+ PRODUCT_TESTS

## 10. Installation rule

Factory Resolver must reject any block when:
- required test is FAIL;
- required test is NOT_RUN;
- evidence is missing;
- threat model is missing;
- compatibility is unknown;
- security gate is not passed;
- residual risk exceeds accepted policy.
