# Business Process
Owner: Senior Business Analyst.

Goal:
convert an admissible source into a structured representation that downstream normalization/chunking can consume without losing where every fragment came from.

Input:
SourceIntakeRecord + APPROVED SourceAdmissibilityDecision + valid ProvenanceRecord + supported source content.

Output:
StructuralDocument with ordered StructuralUnit records.

KPIs:
- units without source trace: 0%;
- reordered units: 0%;
- unsupported format silently accepted: 0%;
- parser diagnostics present on partial/failed parse: 100%.