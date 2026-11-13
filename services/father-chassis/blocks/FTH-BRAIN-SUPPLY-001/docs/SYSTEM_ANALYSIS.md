# SYSTEM_ANALYSIS

## Inputs
- AgentBrainRequest
- tuple[BrainPackageDescriptor]
- BrainSupplyPolicy

## Required request dimensions
agent identity, **agent class A1…A6**, **requested Brain Class B1…B6**, role, domains, required capabilities, supply mode, tenant, authorized classifications.

Agent Class and Brain Class are independent dimensions. No implicit A3→B3 rule exists.

## Package dimensions
package/version, Brain Class, domains, capabilities, supported supply modes, compatible Agent Classes, allowed roles, classification, tenant scope, lifecycle state.

## States
Package lifecycle considered by resolver: QUALIFIED, RELEASED, SUPERSEDED, REVOKED.

## System invariants
- requested Brain Class is evaluated independently from Agent Class compatibility;
- no missing required capability;
- no classification escalation;
- no cross-tenant binding;
- no revoked binding;
- no wrong Brain Class binding;
- no incompatible Agent Class binding;
- input order must not alter identity;
- policy version must affect decision identity.
