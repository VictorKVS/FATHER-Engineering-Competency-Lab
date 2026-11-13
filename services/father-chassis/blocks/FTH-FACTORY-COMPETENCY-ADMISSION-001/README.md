# Competency Admission
Block ID: FTH-FACTORY-COMPETENCY-ADMISSION-001

Purpose: admit a factory agent to an engineering stage only when evidence-based competency meets the minimum stage policy.

Scope:
- stage -> required competency policy;
- agent subject/claim lookup;
- Trust CompetencyEvaluator invocation through FATHER adapter;
- fail-closed admission decision;
- admission evidence binding to workflow stage.

Non-goals:
- redefining competency levels;
- replacing Trust core;
- training agents;
- knowledge-base qualification.

Integration rule:
Trust core stays FATHER-independent. FATHER imports/adapts Trust; Trust never imports FATHER.

Current maturity: B9 QUALIFIED by G7 M5 Competency Admission evidence.