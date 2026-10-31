# Research Question Generator

Research questions are not a fixed questionnaire. They are generated from the complete product and business context.

## Generation chain

`IDEA -> PRODUCT VALUE -> BUSINESS PROCESS -> PROCESS STEP -> DECISION -> INPUT INFORMATION -> ROLE / RESPONSIBILITY -> RISK -> COMPETENCY -> KNOWLEDGE GAP -> RESEARCH QUESTION`

## Question families

The generator must consider:
- product purpose, customer value and KPI;
- process inputs/outputs and handoffs;
- decisions and decision rights;
- actors, roles and responsibilities;
- professional competencies and proficiency levels;
- domain concepts and terminology;
- operating procedures and workflows;
- tools, APIs, systems and data sources;
- normative, legal, security and compliance requirements;
- exceptions and rare cases;
- failure modes and business impact;
- adversarial and abuse cases;
- uncertainty and escalation;
- evidence and source authority;
- data freshness and jurisdiction;
- prompt behavior rules;
- RAG retrieval needs;
- durable KB knowledge;
- deterministic tool requirements;
- training prerequisites;
- curriculum levels;
- benchmark/eval cases;
- A/B/N variables and metrics;
- hard-fail criteria;
- end-to-end acceptance scenarios.

## Traceability rule

Every generated research question must have an origin and downstream use:

`origin artifact -> knowledge gap -> question -> evidence -> claim -> engineering target -> test -> metric`

Questions without traceable origin or downstream use are research noise and should not enter the active research graph.
