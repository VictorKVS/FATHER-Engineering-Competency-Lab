# Stage 29 — Adaptive Brain Router

Stage 29 closes the current FATHER architecture cycle 0–29.

Pipeline:

Task
-> task profile (modality / specialization / complexity)
-> Model Knowledge Base
-> explainable model ranking
-> selected registered Brain
-> Block Registry compatibility
-> Product Factory
-> ready UnifiedAgentRuntime
-> execution

Expected routing:
- simple/light task -> llama-small
- general RAG -> qwen-analysis
- coding -> qwen-coder
- deep reasoning -> deepseek-reasoning
- vision -> blocked until a vision Brain is registered

The router does not hard-code one global best model. It selects the simplest suitable Brain for the task and records the reasons.

After Stage 29 the next work is NOT Stage 30. The next milestone is the primitive release line:
BUILD -> SMOKE TEST -> EVIDENCE -> READY/BLOCKED -> releases/<version>.
