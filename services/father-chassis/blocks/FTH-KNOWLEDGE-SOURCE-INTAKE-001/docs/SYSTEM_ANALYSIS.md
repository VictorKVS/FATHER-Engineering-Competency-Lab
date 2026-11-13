# System Analysis
Owner: Senior System Analyst.

Requirements:
SI-01 stable source_id required.
SI-02 source_class required.
SI-03 title required.
SI-04 locator required.
SI-05 version explicit; UNKNOWN when unavailable.
SI-06 publication/effective dates explicit nullable fields.
SI-07 content_hash mandatory when content bytes are available.
SI-08 hash algorithm = SHA-256 for v1.
SI-09 intake records immutable.
SI-10 duplicate content may reference existing identity but metadata is never silently merged.
SI-11 rights/access status at intake is DECLARED only.
SI-12 downstream cannot treat DECLARED as LEGAL_APPROVED.
SI-13 malformed/empty inputs fail closed.
SI-14 raw copyrighted content is not committed to Git evidence by default.

States:
RECEIVED -> FINGERPRINTED -> INTAKE_READY.
REJECTED terminal.