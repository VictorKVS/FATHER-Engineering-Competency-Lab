# Data and State
Owner: System Analyst + Data Architect.

StructuralDocument immutable.

Trace invariant:
every StructuralUnit source binding equals StructuralDocument source binding.

Ordering invariant:
ordinal strictly increasing from 0.

Hash:
document_hash = SHA-256(canonical parser/version/stable source binding/units).

Stable hash inputs:
- source_id;
- source_content_hash;
- parser_id;
- parser_version;
- ordered structural units.

Trace-only identifiers such as provenance_id and decision_id are intentionally NOT part of document_hash because they may be newly issued for the same semantically identical approved source. They remain attached to StructuralDocument/evidence for audit traceability.

No raw source bytes stored in StructuralDocument.

Reference locator v1:
line:<start>-<end>.