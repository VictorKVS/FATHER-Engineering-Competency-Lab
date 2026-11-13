# Architecture
Owner: Principal/Solution Architect.

FactoryEngineeringWorkflow
        ↓ next StageDefinition
FactoryAgentCatalog
        ↓ owner agent
CompetencyAdmissionGate
        ├─ StageCompetencyPolicyRegistry
        └─ TrustCompetencyAdapter
                ↓
projects/FATHER-TRUST-COMPETENCY-0001
    Subject / Claim / EvidenceRecord
    CompetencyEvaluator
    QualificationDecision

Output:
CompetencyAdmissionDecision -> workflow admission.

Dependency direction:
father-chassis -> Trust adapter/core
Trust core -X-> father-chassis

Role, competency, KB, tool and security gates are independent; no gate substitutes for another.