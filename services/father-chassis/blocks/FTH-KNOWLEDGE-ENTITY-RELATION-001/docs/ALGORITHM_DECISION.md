# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. LLM-only extraction — rejected as reference baseline due nondeterminism.
2. regex-only forever — rejected as production strategy.
3. deterministic rule-based reference extractor behind adapter contract — selected for v1 qualification.
4. LLM/NER/domain extractors — future adapters using same output contract.

Reference algorithm:
1. validate chunk-set lineage and ordering;
2. extract candidate entities by deterministic rule;
3. canonicalize names by trim/case-preserving normalization;
4. deduplicate within extraction set by type+canonical_name;
5. parse explicit relation pattern when both entities exist;
6. bind evidence chunk IDs;
7. assign deterministic confidence values defined by policy;
8. compute entity/relation hashes and extraction_set_hash.

Purpose:
qualify the contract, not claim production-grade NLP quality.