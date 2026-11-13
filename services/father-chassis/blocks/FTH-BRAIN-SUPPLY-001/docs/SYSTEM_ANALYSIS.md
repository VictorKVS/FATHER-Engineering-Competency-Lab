# SYSTEM_ANALYSIS

## Inputs
- AgentBrainRequest
- tuple[BrainPackageDescriptor]
- BrainSupplyPolicy

## Required request dimensions
agent identity, agent class, role, domains, required capabilities, supply mode, tenant, authorized classifications.

## Package dimensions
package/version, brain class, domains, capabilities, supported supply modes, compatible agent classes, allowed roles, classification, tenant scope, lifecycle state.

## States
Package lifecycle considered by resolver: QUALIFIED, RELEASED, SUPERSEDED, REVOKED.

## System invariants
- no missing required capability;
- no classification escalation;
- no cross-tenant binding;
- no revoked binding;
- no wrong-class binding;
- input order must not alter identity;
- policy version must affect decision identity.
