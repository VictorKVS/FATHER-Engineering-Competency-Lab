# INTERFACES_AND_VARIABLES

## AgentBrainRequest
- request_id
- agent_id
- agent_class — класс агента A1…A6
- requested_brain_class — требуемый класс мозга B1…B6
- role
- domains[]
- required_capabilities[]
- supply_mode
- tenant_id
- authorized_classifications[]

## BrainPackageDescriptor
- package_id
- version
- brain_class — класс Brain Package B1…B6
- domains[]
- capabilities[]
- supported_supply_modes[]
- compatible_agent_classes[] — допустимые A-классы агентов
- allowed_roles[]
- classification
- tenant_scope
- lifecycle_state

## BrainSupplyPolicy
- policy_id
- version
- eligible_states[]
- require_exact_brain_class
- allow_global_tenant_packages

## BrainSupplyDecision
- status
- selected_package_id
- selected_version
- decision_id
- decision_hash
- diagnostics[]
