# Architecture
Owner: Principal/Solution Architect.

Repository root
├─ projects/FATHER-TRUST-COMPETENCY-0001
│   └─ package trust_competency
└─ services/father-chassis
    └─ CompetencyAdmission adapter

Install orchestration:
root/CI -> install Trust editable -> install chassis editable.

Runtime import:
father.engineering.competency_admission
        ↓
trust_competency public API only

Forbidden:
- import from Trust private modules when public API is sufficient;
- sys.path changes;
- reverse import from Trust into father;
- source duplication.