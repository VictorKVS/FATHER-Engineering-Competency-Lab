# ALGORITHM_DECISION

## Reference v1

1. Validate request, policy and candidates.
2. Require eligible lifecycle/evidence state.
3. Filter by Brain Class.
4. Filter by deployment profile.
5. Require all requested capabilities.
6. Enforce corpus envelope.
7. Enforce concurrency envelope.
8. Enforce RAM/storage ceilings when supplied.
9. Enforce offline requirement.
10. Enforce HA requirement.
11. Enforce high-assurance requirement.
12. Enforce low-power requirement when power_constrained=true.
13. Rank eligible profiles by:
    - lower operational complexity;
    - lower minimum RAM;
    - lower minimum storage.
14. Equal best profiles → AMBIGUOUS.
15. Emit explanation and deterministic hash.

## Why
The selector prefers the smallest architecture that satisfies the declared requirements.

## Evidence rule
A profile envelope is only eligible when its evidence state is QUALIFIED.

Measured vendor-specific envelopes are added later by benchmark qualification.
