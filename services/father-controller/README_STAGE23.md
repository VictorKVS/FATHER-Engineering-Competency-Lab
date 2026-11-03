# Stage 23 — Real Hybrid RAG

Stage 23 replaces only the Knowledge Slot while keeping the same FATHER agent runtime.

Stack:
- Ollama embedding API
- BGE-M3 multilingual embedding model
- dense semantic cosine similarity
- lexical token overlap
- weighted hybrid fusion
- source/provenance metadata
- structured ContextEnvelope handoff

The stage automatically pulls `bge-m3` if it is absent.

This is real semantic hybrid RAG, but the vector index is still in-memory.
A persistent vector database such as Qdrant/FAISS is a later storage layer and can replace this adapter without rewriting the agent.

Run with `FATHER_UPDATE.ps1`.
