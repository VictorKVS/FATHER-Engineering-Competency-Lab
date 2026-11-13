# SECURITY_MODEL

## Threats
- selecting an unqualified storage envelope;
- silently ignoring HA/security requirements;
- choosing a high-power profile for constrained edge;
- resource ceiling bypass;
- profile downgrade;
- input-order manipulation;
- vendor preference hidden as architecture logic.

## Controls
- fail-closed hard constraints;
- qualified evidence state required;
- deterministic algorithm;
- explicit rejection reasons;
- no vendor identifiers in core selector;
- policy/version-bound decision identity.

## Security note
High Assurance is a hard requirement, not a scoring bonus.
