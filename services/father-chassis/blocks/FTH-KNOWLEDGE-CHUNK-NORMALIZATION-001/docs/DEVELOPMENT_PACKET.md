# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR IMPLEMENTATION.

Approved implementation:
- knowledge_factory/chunk_normalization.py;
- ChunkPolicy;
- NormalizedChunk;
- NormalizedChunkSet;
- ChunkingDecision;
- DeterministicStructuralChunker;
- whitespace normalization;
- heading context;
- deterministic paragraph splitting;
- canonical chunk/chunk-set hashes.

Forbidden:
- embeddings;
- LLM summarization/rewrite;
- cross-document chunking;
- entity extraction;
- retrieval scoring.