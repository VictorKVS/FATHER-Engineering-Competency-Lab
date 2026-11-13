# Interfaces and Variables
Owner: Architect + System Analyst.

Public Trust API required by FATHER:
- Claim
- EvidenceRecord
- QualificationDecision
- Subject
- EvidenceLedger
- CompetencyEvaluator
- CompetencyPolicy

Compatibility variables:
- trust_package_name = "father-trust-competency"
- trust_import_name = "trust_competency"
- supported_trust_api = "0.1.x"
- python_requirement = ">=3.10"

Environment bootstrap:
from repository root:
python -m pip install -e "projects/FATHER-TRUST-COMPETENCY-0001[dev]"
python -m pip install -e "services/father-chassis[dev]"

No runtime environment variable is allowed to inject Trust source paths.