# System Analysis
Owner: Senior System Analyst.

Requirements:
SP-01 parser accepts only APPROVED decision.
SP-02 provenance binding must validate before parse.
SP-03 parser_id and parser_version recorded.
SP-04 StructuralDocument binds source_id/content_hash/provenance_id.
SP-05 StructuralUnit has stable unit_id, ordinal, unit_type, text, locator.
SP-06 unit order preserved.
SP-07 locator identifies original position at available granularity.
SP-08 blank structural units discarded.
SP-09 unsupported media/format -> explicit REJECTED.
SP-10 partial extraction -> PARTIAL with diagnostics.
SP-11 parsing must not mutate source content.
SP-12 parser output hash deterministic for same input/parser version.
SP-13 raw source bytes not embedded into canonical parse evidence.

Supported v1 reference input: plain text/UTF-8 bytes only.
PDF/DOCX/HTML are future adapters.