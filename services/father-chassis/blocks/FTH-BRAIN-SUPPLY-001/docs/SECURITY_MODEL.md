# SECURITY_MODEL

## Threats
- wrong brain supplied to an agent;
- privilege escalation by classification mismatch;
- cross-tenant leakage;
- role/domain confusion;
- revoked package reuse;
- unqualified package binding;
- capability confusion;
- silent fallback to broader brain;
- policy downgrade;
- input-order manipulation;
- ambiguous selection hidden as success.

## Controls
- fail-closed filtering;
- explicit classification authorization;
- tenant matching;
- lifecycle gating;
- exact class v1;
- policy/version-bound hash;
- deterministic sorting;
- explicit AMBIGUOUS state;
- immutable decision output;
- downstream UAG enforcement remains mandatory.

## Non-goal
This block does not grant tool/action authority and does not expose storage credentials.
