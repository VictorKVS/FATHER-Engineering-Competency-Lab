# FATHER AI Library Register

Canonical human-readable view of the FATHER knowledge-source registry.

**Pipeline:** intake -> SHA-256 -> classification -> metadata verification -> knowledge extraction -> chunks -> graph -> evidence -> study -> applied.

> Original copyrighted files are not committed to Git. The repository stores metadata, provenance state and hashes only.

| ID | Type | Source | Year | Domain | Priority | Status |
|---|---|---|---:|---|---|---|
| LIB-AI-001 | BOOK | *Generative AI Security: Theories and Practices* | 2024 | AI Security / Governance / DevSecOps | P0 CORE | Added, metadata verified, file received |
| LIB-AI-002 | BOOK | *Designing Machine Learning Systems* — Chip Huyen | 2022 | ML Systems / MLOps / Production | P0 CORE | Added, metadata verified, file received |
| LIB-AI-003 | BOOK | *Hands-On Large Language Models* — Alammar, Grootendorst | 2024 | LLM / Embeddings / RAG / Fine-tuning | P0 CORE | Added, metadata verified, file received |
| LIB-AI-004 | BOOK_EXCERPT | *AI Engineering* — Chip Huyen | 2025 | Foundation Models / Eval / RAG / Agents | P0 CORE | **Partial: uploaded file has 21 pages** |
| LIB-AI-005 | SLIDES | *From ML Engineering to AI Engineering* — Chip Huyen | 2024 | AI stack / Context / Eval / RAG | P1 SUPPORT | Added, metadata verified, file received |
| LIB-AI-006 | CHECKLIST | *LLM AI Cybersecurity & Governance Checklist* — OWASP | 2024 | LLM Security / TEVV / Governance / Red Team | P0 CORE | Added, metadata verified, file received |
| LIB-AI-007 | PAPER | *Review of Generative AI Methods in Cybersecurity* | 2024 | GenAI / Cybersecurity / Attack & Defense | P0 SCIENTIFIC | Added, metadata verified, file received |

## Distribution by knowledge base

### P02 KNOWLEDGE_CORE
- LIB-AI-003 — LLM fundamentals, embeddings, semantic search, RAG.
- LIB-AI-004 — foundation-model application engineering.
- LIB-AI-005 — AI engineering stack and context construction.

### P03 FATHER KNOWLEDGE FACTORY
- LIB-AI-002 — system lifecycle, data, monitoring, production architecture.
- LIB-AI-003 — retrieval and representation knowledge.
- LIB-AI-004 — evaluation, agents, feedback loops.

### FATHER SECURITY / SECGRAPH / POLYGON
- LIB-AI-001 — GenAI security architecture and governance.
- LIB-AI-006 — operational security/governance checklist and TEVV.
- LIB-AI-007 — scientific cybersecurity review and literature evidence.

## Immediate study order

1. **LIB-AI-004 — AI Engineering**: use uploaded excerpt now; obtain/verify complete source separately before marking the book complete.
2. **LIB-AI-003 — Hands-On Large Language Models**.
3. **LIB-AI-002 — Designing Machine Learning Systems**.
4. **LIB-AI-001 — Generative AI Security**.
5. **LIB-AI-006 — OWASP Checklist**.
6. **LIB-AI-007 — cybersecurity review paper**.
7. **LIB-AI-005 — slides as a visual/index reference**.

## Status policy

Do not mark a source **STUDIED** merely because it was indexed or summarized.
A source reaches **APPLIED_IN_PRACTICE** only when its concepts are demonstrated in a project, test, architecture decision, control, laboratory exercise, or qualification evidence.
