# System Analysis
Owner: Senior System Analyst.

Existing Trust source:
projects/FATHER-TRUST-COMPETENCY-0001

Existing levels:
C0, C1, C2, C3, C4, C5, C6.

Requirements:
CA-01 every controlled factory stage has a minimum competency policy.
CA-02 admission uses Trust CompetencyEvaluator, not a duplicate evaluator.
CA-03 agent_id maps to Trust subject_id.
CA-04 stage policy identifies domain, capability, minimum level, evidence count and required evidence types.
CA-05 missing subject/claim/evidence fails closed.
CA-06 qualified=false blocks stage execution.
CA-07 qualification reasons are preserved.
CA-08 admission decision records stage_id, agent_id, qualification_id and evidence_ids.
CA-09 role ownership must pass independently of competency.
CA-10 competency cannot override tool/security/KB admission.
CA-11 Trust core remains FATHER-independent.

Failure modes:
unknown agent, unknown stage policy, unknown C-level, insufficient evidence, wrong claim domain/capability, Trust adapter unavailable.