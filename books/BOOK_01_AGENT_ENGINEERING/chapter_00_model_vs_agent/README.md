# Chapter 00 — Model is not Agent

## Engineering thesis

An LLM is a probabilistic inference component. It does not by itself provide durable state,
tool execution, permissions, recovery, observability, evidence, or lifecycle control.

FATHER therefore treats a model as a replaceable **Model Slot** inside an agent.

## FATHER Agent Construct

```text
AGENT =
ROLE
+ PROMPT PROGRAM
+ RAG
+ KNOWLEDGE BASE
+ TOOLS
+ MEMORY / STATE
+ CONTRACTS
+ POLICIES
+ MODEL SLOT
+ EVALS
+ EVIDENCE
```

## Baseline experiment

### Research question
What capabilities are supplied by the model and what must be supplied by the harness?

### Baseline A
Single direct LLM call.

### Candidate B
Same model + minimal harness:
- system role;
- message history;
- step limit;
- tool dispatcher;
- trace log.

### Controlled variables
- same model;
- same task;
- same sampling configuration where supported.

### Measurements
- task success;
- number of steps;
- tool-use correctness;
- recovery from tool error;
- reproducibility of trace;
- latency;
- token use.

## PASS condition

This chapter is not PASS merely because code exists.

PASS requires an actual run with evidence showing which capabilities originate from
the model and which are provided by the harness.

## Future Agent V1 contribution

This chapter produces:
- ModelProvider contract;
- minimal AgentLoop contract;
- first experiment manifest;
- trace format;
- baseline evidence.
