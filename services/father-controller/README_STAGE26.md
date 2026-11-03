# Stage 26 — FATHER Product Factory

Stage 26 introduces config-driven assembly of complete agent products.

A Product Spec selects:
- Agent manifest
- Brain Slot
- Competency / Prompt
- Knowledge adapter
- Retrieval settings
- Input adapters
- Output adapters
- Tool slot
- Context Bus

The ProductFactory validates the specification, assembles the product, performs slot health checks, and returns a ready UnifiedAgentRuntime.

Current product examples:
- father-general-single-v1
- father-general-hybrid-v1
- father-coder-single-v1

This is the beginning of the real FATHER production line: one chassis, multiple products.
