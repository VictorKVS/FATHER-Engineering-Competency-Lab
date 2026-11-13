# System Analysis
Owner: Senior System Analyst.

Requirements:
LP-01 consume SourceIntakeRecord only.
LP-02 evaluate configured access/right policy.
LP-03 statuses: APPROVED, HOLD, REJECTED.
LP-04 APPROVED requires explicit allowed_use.
LP-05 APPROVED requires content_hash when source bytes were available at intake.
LP-06 ProvenanceRecord binds source_id, locator, version, content_hash, decision_id.
LP-07 decision records policy_id/version.
LP-08 evidence_refs required for APPROVED.
LP-09 missing/ambiguous policy inputs -> HOLD, not APPROVED.
LP-10 denied rights/access -> REJECTED.
LP-11 downstream processing allowed only on APPROVED.
LP-12 policy engine is deterministic and versioned.
LP-13 no source body copied into provenance evidence.
LP-14 manual/legal exception requires separate evidence ref and authority marker.

Open:
jurisdiction-specific policy content and automated license parsing are future domain packs.