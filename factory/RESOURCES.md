# FATHER Knowledge → Product Resources

This page is inspired by the **resource-index pattern** used in the AI Engineering companion repository, but FATHER extends the idea into an engineering traceability system.

The purpose is not only to answer **what should we read?**

It must also answer:

- what knowledge do we extract?
- what architectural decision does it affect?
- what Factory block/chassis/policy does it become?
- what test proves the implementation?
- in which product is it reused?

> FATHER principle: a source is useful only when its knowledge can be traced into an engineering artifact or an explicit rejected decision.

---

## Navigation

- [0. How to use this map](#0-how-to-use-this-map)
- [1. Product planning](#1-product-planning)
- [2. Foundation models and inference](#2-foundation-models-and-inference)
- [3. Evaluation](#3-evaluation)
- [4. Prompt and context engineering](#4-prompt-and-context-engineering)
- [5. RAG and knowledge systems](#5-rag-and-knowledge-systems)
- [6. Agents and orchestration](#6-agents-and-orchestration)
- [7. Memory and state](#7-memory-and-state)
- [8. Tools, MCP and external actions](#8-tools-mcp-and-external-actions)
- [9. Security and guardrails](#9-security-and-guardrails)
- [10. Observability and feedback](#10-observability-and-feedback)
- [11. DevSecOps and deployment](#11-devsecops-and-deployment)
- [12. Knowledge-to-product matrix](#12-knowledge-to-product-matrix)

---

## 0. How to use this map

Every useful source should follow this lifecycle:

```text
SOURCE
  ↓
KNOWLEDGE EXTRACT
  ↓
REQUIREMENT / PRINCIPLE
  ↓
ADR / DESIGN DECISION
  ↓
FACTORY CAPABILITY
  ↓
BLOCK / CHASSIS / POLICY
  ↓
TEST
  ↓
EVIDENCE
  ↓
PRODUCT
```

Status vocabulary:

- **READ** — source found and reviewed.
- **EXTRACTED** — engineering knowledge written down.
- **MAPPED** — connected to a capability/block/ADR.
- **IMPLEMENTED** — represented in code/configuration.
- **PROVEN** — integration evidence exists.
- **REUSED** — used by more than one product.

---

## 1. Product planning

### Knowledge we need

- when AI is the right solution;
- task decomposition;
- human/AI responsibility boundaries;
- latency, cost, quality and UX trade-offs;
- product feedback loops.

### Factory destination

```text
Knowledge
  → Product Requirements
  → Capability Model
  → Chassis Selection
  → Product Configuration
```

### Current FATHER artifacts

- `factory/products/`
- future `factory/requirements/`
- future Capability Registry
- future Chassis Selector

---

## 2. Foundation models and inference

### Knowledge we need

- model capability differences;
- context limits;
- sampling;
- structured output;
- cost/latency/VRAM;
- local vs cloud inference;
- model routing.

### Factory destination

```text
Model knowledge
  → MODEL capability profile
  → Model Registry
  → Model Router
  → Chassis compatibility
```

### Current target block

- `FTH-BLOCK-MODEL-001` — model router

### Future outputs

- Model Zoo
- inference profiles
- resource requirements
- fallback policies

---

## 3. Evaluation

### Knowledge we need

- task-specific evals;
- LLM-as-a-judge limits;
- benchmark contamination;
- regression evaluation;
- agent evaluation;
- safety evaluation.

### Factory destination

```text
Evaluation research
  → Acceptance Criteria
  → Evaluator Block
  → Test Gate
  → Evidence
```

### Future target blocks

- `FTH-BLOCK-EVAL-001`
- `FTH-BLOCK-BENCH-001`
- `FTH-BLOCK-REGRESSION-001`

No component should reach PRODUCTION without evaluation evidence.

---

## 4. Prompt and context engineering

### Knowledge we need

- instruction hierarchy;
- structured prompts;
- constrained outputs;
- context assembly;
- defensive prompting;
- prompt versioning.

### Factory destination

```text
Prompt research
  → Prompt Contract
  → Context Builder
  → Policy
  → Prompt Registry
  → Regression tests
```

### Future artifacts

- Prompt Registry
- Context Policy
- Prompt Security tests
- Prompt version evidence

---

## 5. RAG and knowledge systems

### Knowledge we need

- retrieval architecture;
- chunking;
- embeddings;
- vector indexes;
- hybrid search;
- reranking;
- provenance;
- graph retrieval;
- freshness.

### Factory destination

```text
RAG knowledge
  → Knowledge Contract
  → Ingestion
  → Index
  → Retrieval
  → Citation / provenance
  → RAG Block
```

### Future target blocks

- `FTH-BLOCK-RAG-INGEST-001`
- `FTH-BLOCK-RETRIEVE-001`
- `FTH-BLOCK-RERANK-001`
- `FTH-BLOCK-KG-001`

Likely products:

- ALINA
- OSINT
- CyberED
- BOOKCRAFT

---

## 6. Agents and orchestration

### Knowledge we need

- ReAct;
- planning;
- tool use;
- multi-agent orchestration;
- handoffs;
- failure modes;
- loops and termination;
- human-in-the-loop;
- agent benchmarks.

### Factory destination

```text
Agent research
  → Agent Contract
  → Runtime
  → Router
  → Workflow / Graph
  → Guardrails
  → Evaluation
```

### Current FATHER artifacts

- `FTH-BLOCK-RUNTIME-001`
- `FTH-BLOCK-ROUTER-001`
- `C1_LIGHT_AGENT`

### Future artifacts

- Agent Zoo
- Workflow Registry
- Multi-Agent chassis `C3_MULTI_AGENT`
- agent compatibility profiles

---

## 7. Memory and state

### Knowledge we need

- short-term state;
- long-term memory;
- episodic/semantic memory;
- retrieval from memory;
- forgetting;
- memory security;
- memory evaluation.

### Factory destination

```text
Memory research
  → Memory policy
  → State interface
  → Memory Block
  → retention tests
```

### Future target blocks

- `FTH-BLOCK-STATE-001`
- `FTH-BLOCK-MEMORY-001`

---

## 8. Tools, MCP and external actions

### Knowledge we need

- function calling;
- tool schemas;
- MCP;
- permissions;
- tool selection;
- tool failures;
- action confirmation;
- sandboxing.

### Factory destination

```text
Tool knowledge
  → Tool Contract
  → Permission Profile
  → Tool/MCP Registry
  → Runtime Adapter
  → Audit
```

### Future target blocks

- `FTH-BLOCK-TOOLS-001`
- `FTH-BLOCK-MCP-001`
- `FTH-BLOCK-SANDBOX-001`

---

## 9. Security and guardrails

### Knowledge we need

- prompt injection;
- indirect prompt injection;
- excessive agency;
- tool abuse;
- data exfiltration;
- authorization;
- sandboxing;
- secrets;
- AI red teaming;
- policy enforcement.

### Factory destination

```text
Security knowledge
  → Threat
  → Security Requirement
  → Security Profile
  → Guardrail / Authorization
  → Security Test
  → Evidence
```

### Current FATHER artifact

- `FTH-BLOCK-GUARD-001`

### Future artifacts

- Security Profile Registry
- threat model per chassis
- AI Antivirus
- POLYGON
- UAG enforcement layer

---

## 10. Observability and feedback

### Knowledge we need

- traces;
- metrics;
- logs;
- agent decisions;
- user feedback;
- cost;
- latency;
- failures;
- quality drift.

### Factory destination

```text
Observability knowledge
  → telemetry contract
  → OBS block
  → dashboards
  → feedback loop
  → regression trigger
```

### Current FATHER artifacts

- `FTH-BLOCK-OBS-001`
- `FTH-BLOCK-AUDIT-001`

---

## 11. DevSecOps and deployment

### Knowledge we need

- reproducible builds;
- CI/CD;
- containerization;
- SBOM;
- dependency scanning;
- secrets scanning;
- deployment rollback;
- runtime isolation;
- evidence retention.

### Factory destination

```text
DevSecOps knowledge
  → Build Policy
  → CI Gate
  → Security Gate
  → Release Manifest
  → Deployment Evidence
```

### Future artifacts

- Build Block
- Release Gate
- SBOM generation
- deployment profile
- rollback evidence

---

## 12. Knowledge-to-product matrix

| Knowledge area | Extracted engineering capability | Factory artifact | Product use | Proof |
|---|---|---|---|---|
| Agent runtime | controlled execution loop | FTH-BLOCK-RUNTIME-001 | HELLO_FACTORY → future agents | contract + smoke |
| Routing | request/agent/model dispatch | FTH-BLOCK-ROUTER-001 | HELLO_FACTORY | contract |
| Model selection | model invocation abstraction | FTH-BLOCK-MODEL-001 | HELLO_FACTORY → Model Zoo | contract |
| Guardrails | allow/deny control | FTH-BLOCK-GUARD-001 | all agent products | contract + deny-path |
| Audit | immutable decision/event trace | FTH-BLOCK-AUDIT-001 | all production products | audit evidence |
| Observability | telemetry and metrics | FTH-BLOCK-OBS-001 | all production products | telemetry evidence |
| RAG | retrieval-backed knowledge | planned RAG blocks | ALINA / OSINT / CyberED | planned |
| Multi-agent orchestration | graph/team execution | planned C3 chassis | POLYGON / OSINT / FATHER teams | planned |
| MCP/tools | standard external actions | planned Tool/MCP Registry | all action agents | planned |
| Security | AI threat controls | Guardrails + future Security Registry | UAG / Antivirus / POLYGON | planned |

---

## Source registry relationship

The human-readable map in this file is backed by machine-readable registries:

- `factory/registry/sources.json`
- `factory/registry/knowledge_map.json`
- `factory/registry/blocks.json`

The intended rule is:

```text
No important knowledge without SOURCE_ID.
No production block without knowledge mapping.
No production claim without evidence.
```

This page is the visual index. The registries are the machine-readable truth.


## BOOK-0001 — Designing Large Language Model Applications

FATHER processing package:

- `factory/knowledge/books/BOOK-0001/`
- source: `SRC-BOOK-0001`
- processing agent: ALINA
- required outputs per chapter: translation → semantic outline → glossary → applications → examples → algorithms → conclusions → combinations → checklists → knowledge atoms → FATHER mapping.

Status: Chapter 1 initial extraction complete; full 13-chapter semantic pass registered.
