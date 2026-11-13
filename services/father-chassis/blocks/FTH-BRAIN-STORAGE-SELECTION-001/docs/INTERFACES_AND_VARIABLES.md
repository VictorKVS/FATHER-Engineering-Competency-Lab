# INTERFACES_AND_VARIABLES

## StorageSelectionRequest
See SYSTEM_ANALYSIS.md.

## StorageProfileDescriptor

`power_class` reference values:
- LOW
- MEDIUM
- HIGH

`evidence_state`:
- DRAFT
- MEASURED
- QUALIFIED
- REVOKED

## StorageSelectionPolicy
- policy_id
- version
- eligible_lifecycle_states[]
- required_evidence_state
- require_exact_brain_class
- require_exact_deployment_profile

## StorageSelectionDecision
- status: SELECTED / NO_MATCH / AMBIGUOUS / REJECTED
- selected_profile_id
- selection_reasons[]
- rejected_alternatives[]
- decision_id
- decision_hash
