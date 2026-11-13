# Data and State
Owner: System Analyst + Data Architect.

All graph snapshot records immutable.

Node identity hash:
entity_type + canonical_name + sorted source entity lineage + sorted evidence lineage + policy identity.

Edge identity hash:
relation_type + resolved subject/object node IDs + sorted source relation lineage + sorted evidence lineage + policy identity.

Graph hash:
sorted source extraction identities + ordered node hashes + ordered edge hashes + ordered conflict payloads + policy identity.

Input ordering must not affect graph_hash.

No raw source text stored in graph snapshot.