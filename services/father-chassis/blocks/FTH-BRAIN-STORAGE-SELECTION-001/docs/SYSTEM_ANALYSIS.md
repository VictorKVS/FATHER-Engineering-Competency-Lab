# SYSTEM_ANALYSIS

## Input — StorageSelectionRequest
- request_id
- brain_class
- deployment_profile
- required_capabilities[]
- corpus_chunks
- concurrent_users
- target_p95_ms
- max_ram_mb
- max_storage_gb
- offline_required
- high_availability_required
- high_assurance_required
- power_constrained

## Candidate — StorageProfileDescriptor
- profile_id
- supported_brain_classes[]
- deployment_profiles[]
- capabilities[]
- min_ram_mb
- min_storage_gb
- max_corpus_chunks
- max_concurrent_users
- supports_offline
- supports_ha
- supports_high_assurance
- power_class
- operational_complexity
- lifecycle_state
- evidence_state

## Output — StorageSelectionDecision
- status
- selected_profile_id
- selection_reasons[]
- rejected_alternatives[]
- decision_id
- decision_hash

## Invariants
- no profile violating a hard constraint may be selected;
- unqualified profile envelopes are not accepted by reference policy;
- operator explanation is mandatory;
- candidate input order cannot affect result;
- policy version changes identity;
- no vendor is selected by this block.
