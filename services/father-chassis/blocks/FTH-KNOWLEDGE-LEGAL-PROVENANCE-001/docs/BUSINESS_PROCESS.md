# Business Process
Owner: Senior Business Analyst.

Goal:
only sources with an explicit admissibility decision and verifiable provenance may proceed into Knowledge Factory processing.

Input:
SourceIntakeRecord + source-policy context + supporting evidence.

Output:
SourceAdmissibilityDecision + ProvenanceRecord.

Business rules:
- DECLARED rights are not approval;
- missing rights/access evidence -> HOLD/BLOCK;
- allowed use must be explicit;
- provenance must bind the exact source content hash/version/locator;
- rejected/held sources do not reach parser/chunker.

KPIs:
- source processed without admissibility decision: 0%;
- source processed without provenance: 0%;
- decision traceable to source hash: 100%;
- ambiguous rights silently accepted: 0%.