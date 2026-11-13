# Data and State
Owner: System Analyst + Data Architect.

Registry primary key:
source_id.

Secondary index:
content_hash -> source_id(s).

Record immutable after INTAKE_READY.
Corrections create a new record/version or explicit superseding relation.

Git stores metadata/contracts/evidence references only.
Raw copyrighted/proprietary source bytes stay outside repository unless rights explicitly permit storage.

Future:
dedicated source registry + object-store reference.