# FUA-001 — Reference Agent OSINT Study

Status: RESEARCHED / DESIGN CANDIDATE
Date: 2026-11-01

## Mission

Create one universal FATHER agent chassis that can become ALINA, OSINT Analyst, TIMA, Security Analyst, Legal Analyst or another specialist by replacing intelligence packs instead of rewriting the runtime.

## Military numbering standard

All FUA architecture uses stable hierarchical numbering.

## 01. Candidate field

### 01.01 Pydantic AI + Harness
Primary candidate.

Strengths:
- Python-native;
- model/provider abstraction;
- reusable capabilities;
- tools and MCP;
- planning, memory, skills, subagents and guardrails in Harness;
- structured/typed contracts;
- durable execution integrations;
- separate eval package;
- compatible with FastAPI/Pydantic engineering style.

Role in FUA:
REFERENCE CHASSIS.

### 01.02 LangGraph
Strengths:
- durable execution;
- checkpoints;
- persistence;
- human-in-the-loop;
- deterministic + agentic graph composition.

Weakness:
- orchestration runtime, not complete universal agent definition.

Role in FUA:
WORKFLOW / STATE REFERENCE, optional adapter.

### 01.03 Letta / MemGPT
Strengths:
- stateful identity;
- long-term memory;
- self-editing memory/skills;
- hierarchical memory concepts;
- persistent agent experience.

Weakness:
- current active harness is strongly opinionated and TypeScript-oriented compared with our Python core.

Role in FUA:
MEMORY / LEARNING REFERENCE.

### 01.04 OpenAI Agents SDK
Strengths:
- lightweight agent loop;
- tools/MCP;
- guardrails;
- sessions;
- tracing;
- human-in-loop;
- handoffs / agents-as-tools;
- provider-agnostic support exists.

Weakness:
- default ecosystem is OpenAI-centered; FATHER must remain provider-independent at contract level.

Role in FUA:
GUARDRAIL / TOOL / TRACE REFERENCE.

### 01.05 Microsoft AutoGen
Rejected as foundation:
- repository archived and no longer maintained.
- useful historically for multi-agent patterns only.

## 02. Scientific behavior patterns

### 02.01 ReAct
Interleave reasoning and actions. Use as the default task loop pattern, but keep internal reasoning private and persist only decisions/evidence/actions.

### 02.02 Reflexion
Use verbal feedback and episodic memory to improve later attempts without weight updates.

### 02.03 CRITIC
Use external tools/evaluators to check and repair outputs.

### 02.04 Toolformer principle
A model should decide when a tool is appropriate, while FUA Policy Engine decides whether the call is permitted.

### 02.05 MemGPT principle
Separate working context from durable external memory; context window is a cache, not the entire agent memory.

### 02.06 AgentBench lesson
Long-horizon reasoning, decision-making and instruction following are major agent failure modes; POLYGON must test these explicitly.

### 02.07 SWE-agent lesson
Agent-computer interface design strongly affects task success; tools must be designed for agents, not simply exposed raw.

## 03. FUA-001 selected architecture

FUA-001 is NOT a fork of Pydantic AI.

FUA-001 uses:
- Pydantic AI concepts as the main implementation reference;
- LangGraph concepts for durable graph/state;
- Letta/MemGPT concepts for memory;
- ReAct/Reflexion/CRITIC for behavior loops;
- FATHER contracts for security, evidence and portability.

## 04. FUA CORE

01. Identity
02. Role
03. Goal
04. Task Planner
05. State
06. Memory
07. Prompt Runtime
08. RAG Runtime
09. Knowledge Runtime
10. Tool Runtime
11. Model Router
12. Policy Engine
13. Evaluator
14. Audit
15. Observability

## 05. Extended chassis

16. Skill Runtime
17. Context Manager
18. Reflection / Learning
19. Human Approval
20. Execution Sandbox
21. Cost / Resource Controller
22. Evidence Manager
23. Compatibility Manager
24. Failure Recovery
25. Release / Readiness Gate

## 06. Core execution loop

MISSION
→ 01 Identity / 02 Role / 03 Goal
→ 12 Policy pre-check
→ 04 Planner
→ 09 Knowledge + 08 RAG
→ 11 Model Router
→ 10 Tool Runtime when needed
→ 13 Evaluator
→ 18 Reflection/Repair
→ repeat if bounded retry is allowed
→ 22 Evidence
→ 14 Audit
→ 15 Observability
→ 25 Readiness/Result

## 07. Swappable model contract

Every model adapter must expose:
- model_id;
- provider;
- local_or_remote;
- context_window;
- structured_output;
- tool_calling;
- embeddings;
- reasoning_profile;
- latency_profile;
- cost_profile;
- privacy_profile;
- safety_profile;
- supported_modalities;
- health_check.

The agent must not contain provider-specific business logic.

## 08. Intelligence Pack

A specialization is loaded as:

ROLE PACK
+ PROMPT PACK
+ KNOWLEDGE PACK
+ RAG PROFILE
+ SKILL PACK
+ TOOL PACK
+ POLICY PROFILE
+ TEST SUITE

Examples:
FUA-001 + ALINA_PACK = ALINA
FUA-001 + OSINT_PACK = OSINT Analyst
FUA-001 + TIMA_PACK = TIMA

## 09. Required POLYGON tests

01. task completion
02. instruction following
03. long-horizon planning
04. model substitution
05. prompt regression
06. RAG retrieval quality
07. tool selection
08. tool permission violation
09. hallucination / unsupported claim
10. contradiction handling
11. memory retention
12. memory pollution
13. adversarial prompt
14. recovery after tool/model failure
15. cost limit
16. latency limit
17. evidence completeness
18. audit completeness
19. human-approval boundary
20. cross-model reproducibility

## 10. Decision

REFERENCE IMPLEMENTATION: Pydantic AI + Harness

ADOPT MODE: ADAPT, NOT FORK BLINDLY.

FATHER owns:
- contracts;
- registries;
- security policy;
- Model Router;
- evidence;
- POLYGON tests;
- intelligence packs.

Third-party framework components remain replaceable behind adapters.
