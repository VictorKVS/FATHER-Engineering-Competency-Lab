# Stage 22 — Unified Single-LLM Agent Runtime

Goal: prove one complete FATHER agent assembled from replaceable slots.

Pipeline:

Input Adapter -> Context Envelope -> Prompt Slot -> Knowledge/Retrieval Slot -> Tool Slot -> Brain Slot -> Output Adapter

Stage 22 deliberately uses one LLM: qwen-analysis / qwen2.5:7b.

It proves:
- API and File input adapters
- JSON and File output adapters
- loaded Prompt Slot
- loaded Knowledge Slot
- retrieval injection into the model context
- Tool Slot result injection
- structured ContextEnvelope / handoff-ready state
- swappable Brain Slot contract

Current retrieval is explicitly labelled lexical-bootstrap. It is NOT yet semantic/vector RAG.
The next RAG stage can replace only the Knowledge adapter without rewriting the agent runtime.

Run with FATHER_UPDATE.ps1.
