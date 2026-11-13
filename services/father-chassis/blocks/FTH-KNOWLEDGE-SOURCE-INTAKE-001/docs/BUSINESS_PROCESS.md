# Business Process
Owner: Senior Business Analyst.

Goal:
ensure no source enters Knowledge Factory anonymously, without a stable identity, version, locator and content fingerprint.

Actors:
source provider/uploader, Knowledge Factory, legal/access validator, provenance subsystem.

Input:
file, URL, document reference, API object, repository object or other supported source candidate.

Output:
SourceIntakeRecord.

KPIs:
- accepted source without source_id: 0%;
- accepted source without locator: 0%;
- accepted source without content hash/fingerprint when bytes are available: 0%;
- duplicate source bytes detected deterministically: 100%;
- downstream handoff traceable to exact intake record: 100%.