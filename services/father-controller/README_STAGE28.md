# Stage 28 — Model Knowledge Base + Applicability Engine

FATHER now stores model knowledge separately from runtime configuration.

The KB records:
- modality
- context window
- strengths
- weaknesses
- recommended complexity levels
- latency/resource class
- vendor/source notes
- local empirical evidence
- decision ladder / escalation policy

The applicability engine classifies a task by:
- modality
- specialization
- complexity

and returns an explainable ranking with reasons.

Selection principle:
Use the simplest model that safely satisfies the task. Escalate only when specialization, complexity, modality, or observed quality requires it.

Examples:
- simple edge transformation -> llama-small
- general/RAG analysis -> qwen-analysis
- coding -> qwen-coder
- deep reasoning -> deepseek-reasoning
- vision -> vision-capable candidates only

The KB and empirical evidence are intentionally separate so FATHER can learn from future benchmarks without rewriting model facts.
