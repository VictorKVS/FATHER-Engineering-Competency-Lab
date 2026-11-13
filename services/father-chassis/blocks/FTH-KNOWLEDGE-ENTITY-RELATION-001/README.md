# Knowledge Entity / Relation Extraction
Block ID: FTH-KNOWLEDGE-ENTITY-RELATION-001

Purpose: extract typed entities and relations from qualified normalized chunks while preserving exact evidence lineage to source chunks.

Scope:
- entity schema;
- relation schema;
- extraction adapter contract;
- confidence/evidence;
- deterministic reference extractor;
- chunk/source lineage;
- extraction-set hash.

Non-goals:
- entity resolution across documents;
- graph persistence;
- embeddings;
- free-form LLM extraction as authoritative default;
- knowledge inference beyond observed chunk evidence.

Current maturity: B9 QUALIFIED by G7 K5 Entity/Relation Extraction evidence.