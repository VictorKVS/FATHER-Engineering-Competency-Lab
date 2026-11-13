# ALGORITHM_DECISION

## Reference v1 algorithm

1. Validate policy and request.
2. Sort candidates by stable package identity.
3. Filter lifecycle eligibility.
4. Require exact Brain Class.
5. Require compatible agent class.
6. Enforce tenant scope.
7. Enforce classification authorization.
8. Enforce supply mode.
9. Enforce domain coverage.
10. Enforce capability coverage.
11. Enforce role restrictions.
12. Rank remaining candidates by:
   - exact tenant preference;
   - capability excess count;
   - stable package/version identity.
13. If none remain → NO_MATCH.
14. If best rank is shared by different packages and tie-break is not policy-authorized → AMBIGUOUS.
15. Emit deterministic decision hash bound to request, selected package and policy version.

## Why deterministic rules first
The first qualification must prove policy semantics without LLM/embedding uncertainty. Probabilistic recommendation may be added later as an advisory layer but may not override authorization.
