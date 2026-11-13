# Human Approval Gate
Block ID: FTH-CORE-APPROVAL-001

Purpose: enforce explicit human authority for actions that policy marks as approval-required.

Scope: request pending approval; restore state; approve existing request; validate action-bound approval; persist through StateStore.

Non-goals: user identity proofing, MFA, organizational approval hierarchy, expiration/revocation, distributed quorum.

Dependencies: FactoryExecutor/ChassisRuntime upstream; StateStore persistence; audit/qualification downstream.

Current maturity: B9 QUALIFIED by G7 M2 persistent lifecycle evidence.