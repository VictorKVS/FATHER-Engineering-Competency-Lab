# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR IMPLEMENTATION.

Approved implementation:
- knowledge_factory/source_intake.py;
- SourceCandidate;
- SourceIntakeRecord;
- SourceIntakeDecision;
- SourceIntakeRegistry protocol;
- InMemorySourceIntakeRegistry reference;
- SHA-256 fingerprinting;
- duplicate-content signal;
- no legal approval semantics.

Forbidden:
- parsing/chunking in this block;
- storing raw copyrighted sources in Git artifacts;
- marking source LEGAL_APPROVED;
- silently merging duplicate metadata.