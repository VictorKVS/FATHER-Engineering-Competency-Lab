# System Analysis
Owner: Senior System Analyst.

Requirements:
WF-01 assign workflow_id.
WF-02 persist all accepted StageArtifacts.
WF-03 persist PASS/BLOCKED StageResults.
WF-04 restore workflow on construction.
WF-05 preserve available_stage after restart.
WF-06 validate restored artifact hashes.
WF-07 reject corrupted/tampered persisted artifact.
WF-08 keep existing in-memory mode when no StateStore is supplied.
WF-09 isolate workflow instances by workflow_id.

NFR:
fail closed; deterministic restore; backend-independent StateStore; no father-controller dependency.

Failure modes:
missing snapshot -> empty workflow;
malformed snapshot -> explicit failure;
hash mismatch -> explicit failure;
unknown stage data -> explicit failure.

Open: distributed writers and snapshot transactions.