# ALINA Scientific Prompt & RAG Engineering Lab

## Principle

Prompt and RAG are engineered artifacts, not hand-written text fragments.

Every promoted Prompt/RAG package must have:
- baseline;
- version;
- train/validation/test split;
- metrics;
- reproducible experiment configuration;
- evidence;
- regression test;
- security test;
- promotion decision.

## Prompt stack

Primary:
1. DSPy as declarative LM-program layer.
2. GEPA as reflective/Pareto optimizer.
3. MIPROv2 as Bayesian instruction + few-shot optimizer.

Research/secondary:
- TextGrad for textual-gradient optimization of compound systems.
- OPRO and PromptBreeder as alternative evolutionary/optimizer baselines.

FATHER-owned layer:
- Prompt Registry
- Prompt Tournament
- Prompt Champion/Challenger
- overfitting detection
- adversarial suite
- model-specific prompt profiles
- evidence + passport integration

## RAG stack

No single RAG algorithm is universal.

Base path:
BM25 + dense retrieval + fusion + reranking.

Optional strategies selected by query/task:
- Contextual Retrieval
- ColBERTv2 late interaction
- HyDE
- GraphRAG
- RAPTOR
- Self-RAG
- Corrective RAG

FATHER-owned layer:
- Retrieval Strategy Router
- Source Trust / Freshness / Version / Jurisdiction
- Evidence Graph
- Citation Traceability
- Retrieval Failure Detector
- Corrective fallback
- RAG Champion/Challenger

## Evaluation

Use Ragas-compatible metrics plus classical IR:
- context precision/recall
- MRR / nDCG / Recall@k
- faithfulness
- factual correctness
- answer relevancy
- citation correctness/completeness
- latency/resource/cost
- security metrics

## Experimental rule

When optimizing Prompt, freeze RAG.
When optimizing RAG, freeze Prompt/model.
When comparing models, freeze Prompt/RAG/tools.
Only then can causality be attributed to the changed component.
