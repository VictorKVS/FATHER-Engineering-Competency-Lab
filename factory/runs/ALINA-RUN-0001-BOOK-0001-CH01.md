# ALINA KNOWLEDGE EXTRACTION RUN-0001

**Source:** `SRC-BOOK-0001`  
**Book:** *Designing Large Language Model Applications* — Suhas Pai  
**Run scope:** Preface + Chapter 1  
**Purpose:** Prove the first end-to-end FATHER knowledge-production chain.

## Pipeline

```text
BOOK
  ↓
ALINA SOURCE READER
  ↓
CLAIM / CONCEPT EXTRACTION
  ↓
NORMALIZATION
  ↓
CAPABILITY MAPPING
  ↓
ADR / FACTORY DECISION
  ↓
BLOCK / CHASSIS TARGET
  ↓
TEST / EVIDENCE TARGET
  ↓
PRODUCT DESTINATION
```

## Extracted knowledge

| ID | Source knowledge | FATHER interpretation | Destination |
|---|---|---|---|
| KNOW-BOOK0001-CH01-001 | Prototype != production | add production readiness gate | Factory core |
| KNOW-BOOK0001-CH01-002 | PDF QA is a multi-stage pipeline | split RAG into standard blocks | C2 / RAG family |
| KNOW-BOOK0001-CH01-003 | similarity retrieval != answer relevance | require retrieval evaluation/reranking | RAG evaluation |
| KNOW-BOOK0001-CH01-004 | model choice depends on use case/cost/evals | capability-aware Model Router | Model Zoo / Router |
| KNOW-BOOK0001-CH01-005 | tools/APIs + task decomposition enable agents | separate Tool/MCP and orchestration layers | Agent chassis |

## Important source boundary

This run only records claims supported by the book scope reviewed. It does not silently add external best practices.

External validation and GitHub candidate selection are a separate later stage:

```text
BOOK CLAIM
  -> extracted knowledge
  -> candidate search
  -> compare implementations
  -> REUSE / ADAPT / BUILD
```

## First product impact

### Existing block strengthened

`FTH-BLOCK-MODEL-001`

Needs future metadata:

- capability profile;
- cost profile;
- context limits;
- evaluation evidence;
- fallback compatibility.

### New planned block families

- Production Readiness Gate
- Evaluator
- RAG Parser
- Chunker
- Embedding
- Vector Store Adapter
- Retriever
- Reranker
- Retrieval Evaluator
- Tool/MCP Runtime

## Factory learning result

The first run demonstrates the intended principle:

> ALINA does not summarize a book for storage. ALINA converts source material into traceable engineering knowledge that FATHER can place into architecture and later connect to reusable implementations.
