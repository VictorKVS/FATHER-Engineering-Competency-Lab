# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. trust declared_rights string — rejected.
2. free-form LLM legal judgement — rejected for authority and determinism.
3. deterministic rule/policy evaluation over declared access/rights + evidence — selected.
4. external policy engine/OPA — future replaceable implementation.

Algorithm v1:
1. validate intake record;
2. select SourceUsePolicy by policy_id/version;
3. normalize declared_access/declared_rights;
4. evaluate deny rules first;
5. evaluate allow rules with required evidence;
6. unresolved/unknown -> HOLD;
7. denied -> REJECTED;
8. allowed -> APPROVED with allowed_use;
9. create immutable ProvenanceRecord binding source hash/locator/version/decision.

Complexity O(number of policy rules).