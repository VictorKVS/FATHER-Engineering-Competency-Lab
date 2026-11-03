# Stage 24 — Automatic Brain Experiments

Stage 24 benchmarks interchangeable Brain Slot implementations under frozen conditions.

For every competency test:
- the task is fixed
- the Prompt Slot is fixed
- the Knowledge/RAG context is prepared once and fixed
- the rubric is fixed
- only the Brain Slot changes

Brains:
- qwen-analysis
- llama-small
- qwen-coder
- deepseek-reasoning

Ranking priority:
1. fewer runtime errors
2. higher pass rate
3. higher average deterministic quality score
4. lower average latency

The original Brain is restored after the experiment.

This does not permanently change the production default Brain. The winner is evidence for later promotion, not an automatic production mutation.
