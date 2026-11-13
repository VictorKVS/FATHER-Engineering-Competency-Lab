# BUSINESS_PROCESS

## Trigger
An agent, workflow or product requires a knowledge capability.

## Flow
1. Product/Agent configuration creates a BrainSupplyRequest.
2. Resolver receives qualified package candidates.
3. Policy filters unauthorized/incompatible packages.
4. Resolver selects one minimal sufficient eligible package or fails closed.
5. Binding decision is emitted with deterministic identity and diagnostics.
6. Downstream Knowledge Access/UAG uses the binding; direct DB access is outside this block.

## Business outcome
Repeatable agent provisioning without rebuilding knowledge infrastructure per agent.

## Failure outcome
NO_MATCH / AMBIGUOUS / REJECTED. No automatic “nearest” package is substituted.
