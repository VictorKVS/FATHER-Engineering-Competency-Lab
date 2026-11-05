# FATHER Semantic Acceptance Gate / Critic MVP-06

Purpose: semantic quality control after runtime execution.

Judge: qwen-analysis / qwen2.5:7b.

The judge sees only task, candidate answer, and caller-supplied context/source.
It scores factual accuracy, source grounding, task fulfillment, completeness,
uncertainty handling, hallucination resistance, and internal consistency.

Acceptance requires score >= 70, key dimensions >= 3, and no critical error.

MVP-06 is standalone. The next stage wires it into the existing 3B -> 7B escalation path.

Run:
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_SEMANTIC_GATE_MVP06.ps1
