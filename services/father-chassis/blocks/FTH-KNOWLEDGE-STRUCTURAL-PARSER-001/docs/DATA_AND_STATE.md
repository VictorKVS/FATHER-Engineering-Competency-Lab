# Data and State
Owner: System Analyst + Data Architect.

StructuralDocument immutable.

Trace invariant:
every StructuralUnit source binding equals StructuralDocument source binding.

Ordering invariant:
ordinal strictly increasing from 0.

Hash:
document_hash = SHA-256(canonical parser/version/source binding/units).

No raw source bytes stored in StructuralDocument.

Reference locator v1:
line:<start>-<end>.