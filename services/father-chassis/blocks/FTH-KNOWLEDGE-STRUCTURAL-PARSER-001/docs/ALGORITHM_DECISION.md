# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. semantic LLM parser first — rejected for determinism.
2. fixed-size character splitting — rejected as structural parser.
3. deterministic line/heading structural parser — selected for v1.
4. format-specific PDF/DOCX/HTML parsers — future adapters.

Algorithm v1:
1. verify admissibility/provenance;
2. decode UTF-8;
3. normalize line endings;
4. detect heading lines deterministically;
5. accumulate paragraph text between blank lines/headings;
6. emit ordered units;
7. compute structural_document_hash;
8. emit diagnostics on decode/unsupported/empty cases.