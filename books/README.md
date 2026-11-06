# FATHER Engineering Books

FATHER books are original engineering textbooks built from:
- course work;
- scientific papers;
- public technical documentation;
- open-source implementations;
- controlled experiments performed in FATHER.

They do **not** reproduce source books. Each chapter converts source ideas into:
1. engineering explanation;
2. algorithm;
3. reference implementation;
4. alternative implementations;
5. tests;
6. metrics;
7. experiment;
8. evidence;
9. promoted/rejected component decisions.

## Books

### BOOK-01 — Agent Engineering
Build an agent from model call to production-qualified agent.

### BOOK-02 — Scientific Prompt, RAG & Knowledge Engineering
ALINA intelligence engineering: Prompt, RAG, KB, evidence and evaluation.

### BOOK-03 — Model Engineering & Selection Lab
Model Zoo, qualification, tournaments, routing, cascades, ensembles and Champion/Challenger.

## Standard chapter layout

```text
chapter_NN/
├── README.md          # original chapter text
├── chapter.yaml       # machine-readable metadata for site
├── algorithms/        # formal algorithms
├── code/              # executable reference implementations
├── experiments/       # A/B/N experiments
├── tests/             # deterministic + model eval tests
└── evidence/          # measured results
```

## Promotion path

SOURCE
→ CLAIM/PATTERN
→ ALGORITHM
→ IMPLEMENTATION
→ EXPERIMENT
→ METRICS
→ VERIFIED / REJECTED / PARETO
→ FATHER COMPONENT REGISTRY
→ AGENT V1 / PRODUCT

The website should consume book.yaml/chapter.yaml rather than hard-code navigation.
