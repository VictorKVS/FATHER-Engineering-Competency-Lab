# FATHER Agent/Model Ramp-Up Plan

## Principle

Increase only one complexity dimension at a time.

Do not start with:
- many agents;
- many models;
- many tools;
- many workflows;
- many domain packs.

Start with one proven execution cell:

`1 AGENT + 1 MODEL + 1 CONTRACT + 1 TEST + 1 EVIDENCE RECORD`

## Phase A — Single Cell

Target:
- one agent;
- one local model;
- no tools except deterministic runtime plumbing;
- one input contract;
- one output contract;
- one Stage 000 task;
- one eval;
- one evidence record.

Exit gate:
- model server READY;
- prompt/chat template works;
- output parses;
- contract passes;
- evidence saved;
- same input produces reproducible result within tolerance.

## Phase B — Same Agent, Multiple Models

Keep agent/prompt/RAG/tools/contracts fixed.
Change only model.

Goal:
- compare GigaChat3 vs Qwen vs other local candidates;
- measure quality/latency/RAM/VRAM/reliability;
- choose Best Known Configuration.

Exit gate:
- same-contract A/B/N complete;
- one promoted primary model;
- at least one fallback model.

## Phase C — Multiple Agents, One Model Policy

Add agents one at a time:
1. AG-000 Product Manager
2. AG-001 ALINA
3. AG-010 OSINT
4. AG-002 Security
5. AG-004 CODEX
6. AG-006 Test Engineer
7. AG-003 TIMA
8. AG-009 Polygon

Each new agent must first work alone before handoff integration.

## Phase D — Agent Handoffs

Connect only two agents first.

Pattern:
`Agent A -> validated handoff -> Agent B -> validated result -> evidence`

Only after two-agent chains pass, build three-agent and workflow chains.

## Phase E — Tools and RAG

Add tools one at a time after agent/model core is stable.

Order:
1. deterministic local files
2. GitHub
3. structured APIs
4. RAG/vector retrieval
5. browser/web
6. messengers/OSINT collectors

## Phase F — Full Factory

Only after previous phases:
- multi-agent orchestration;
- model routing;
- tool routing;
- A/B engine;
- experience store;
- optimization;
- Polygon;
- release gate.

## Engineering rule

If a failure appears after adding one dimension, roll back that dimension and diagnose before adding another.
