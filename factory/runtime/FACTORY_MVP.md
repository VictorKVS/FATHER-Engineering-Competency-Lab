# FATHER Factory MVP

## Goal
Build the smallest complete factory capable of running one product through one stage with one interchangeable LLM and auditable evidence.

## MVP chain

PRODUCT FIELD
→ STAGE SELECTOR 000–100
→ AGENT REGISTRY
→ STAGE PACKAGE LOADER
→ PROMPT/RAG/KB CONTEXT BUILDER
→ MODEL ROUTER
→ LOCAL LLM ADAPTER
→ OUTPUT SCHEMA VALIDATOR
→ EVAL ENGINE
→ A/B COMPARATOR
→ ARTIFACT/EVIDENCE STORE
→ PRODUCT DOSSIER
→ STAGE GATE

## MVP-0 target
Stage 000 IDEA.

## MVP-1 target
Stage 001 Product Discovery.

## Required services/modules

### Control plane
- Product State
- Stage Registry
- Agent Registry
- Model Registry
- Gate Engine
- Handoff Router

### Execution plane
- Context Builder
- Reference Runtime
- Local LLM Adapter
- Schema Validator
- Eval Runner
- AB Comparator

### Evidence plane
- Run Record
- Artifact Registry
- Evidence Index
- Experience Store
- GitHub persistence

### UI
- Product Field
- 000–100 stage rail
- status colors
- proof lamps R/E/L/A
- Product Dossier
- Specialist Workspace
- Run/Evidence view

## MVP acceptance
A synthetic idea can be:
1. entered;
2. processed by reference runtime;
3. processed by local LLM;
4. validated against the same contract;
5. compared A/B;
6. recorded with metrics;
7. promoted or rejected by gate;
8. replayed from saved artifacts.

Until all eight are demonstrated, the Factory MVP is not PASS.
