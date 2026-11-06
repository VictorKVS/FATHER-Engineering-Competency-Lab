# FUA-001 / 07.Prompt Runtime — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 07.01 Purpose

Build, version, validate and execute prompts as controlled engineering artifacts rather than ad-hoc strings.

## 07.02 Required fields

07.01 System Prompt
07.02 Role Prompt
07.03 Task Prompt
07.04 Tool Prompt
07.05 RAG Prompt
07.06 Critic Prompt
07.07 Repair Prompt
07.08 Prompt Registry
07.09 Prompt Versioning
07.10 Model Compatibility
07.11 Prompt Injection Protection
07.12 Prompt Regression Tests

## 07.03 Contract

Inputs:
- trusted Identity/Role/Goal
- selected prompt pack
- bounded context
- retrieved knowledge
- tool schemas
- selected model profile
- policy constraints

Outputs:
- assembled prompt/message set
- prompt version/hash
- compatibility result
- injection risk flags
- execution metadata

Invariants:
- system/role/policy instructions have explicit precedence;
- untrusted content is clearly separated from instructions;
- prompt pack is versioned;
- model compatibility is tested;
- prompts cannot silently change permissions;
- secrets are not interpolated unless explicitly allowed;
- retrieved content cannot become system authority;
- full prompt assembly is reproducible from evidence.

## 07.04 Initial threats

T01 direct prompt injection
T02 indirect prompt injection via RAG/web/file
T03 role hijacking
T04 instruction precedence confusion
T05 secret leakage in prompt
T06 prompt drift after model update
T07 hidden prompt mutation
T08 unsafe tool instruction injection
T09 context smuggling
T10 oversized context evicts critical policy
T11 malicious few-shot/example poisoning
T12 model-specific prompt incompatibility

## 07.05 Draft controls

C01 structured message roles
C02 instruction/data separation
C03 source trust labels
C04 prompt registry + hash
C05 immutable system/policy layer
C06 secret redaction
C07 model compatibility matrix
C08 regression suite
C09 injection detector/heuristics
C10 context-budget reservation for critical policy
C11 template schema validation
C12 provenance of every injected context segment
C13 allowlisted dynamic variables
C14 prompt diff audit

## 07.06 Draft test block

### Functional
PROMPT-T001 system/role/task layers assemble deterministically
PROMPT-T002 variables render correctly
PROMPT-T003 prompt version/hash generated
PROMPT-T004 model compatibility resolved
PROMPT-T005 critic/repair prompts selectable by workflow

### Contract
PROMPT-T010 unknown variable rejected
PROMPT-T011 malformed template rejected
PROMPT-T012 unknown prompt version rejected
PROMPT-T013 incompatible model/prompt pair blocked or downgraded
PROMPT-T014 missing mandatory system layer rejected

### Security
PROMPT-T020 direct prompt injection resisted
PROMPT-T021 indirect injection from RAG treated as data
PROMPT-T022 web/file instruction cannot override system policy
PROMPT-T023 tool output cannot add permissions
PROMPT-T024 secret variable not exposed in unauthorized prompt
PROMPT-T025 role hijack attempt detected
PROMPT-T026 malicious example cannot alter policy
PROMPT-T027 context overflow cannot evict mandatory security instructions
PROMPT-T028 prompt mutation produces audited version/diff
PROMPT-T029 untrusted dynamic variable escaped/validated

### Regression
PROMPT-T030 same prompt pack across model versions benchmarked
PROMPT-T031 prompt drift detected
PROMPT-T032 fallback model compatibility tested
PROMPT-T033 translated/localized prompt behavior tested where applicable
PROMPT-T034 structured-output contract preserved after model swap

### Integration
PROMPT-T040 Role feeds authoritative role layer
PROMPT-T041 Goal feeds bounded task layer
PROMPT-T042 RAG context carries source labels
PROMPT-T043 Tool Runtime schemas injected without executable hidden text
PROMPT-T044 Policy Engine restrictions remain highest authority
PROMPT-T045 Audit stores prompt version/hash not just free-form result
PROMPT-T046 Evaluator links result to exact prompt/model pair

### POLYGON draft
PROMPT-T060 OWASP-style indirect injection document
PROMPT-T061 malicious webpage says ignore previous instructions
PROMPT-T062 poisoned few-shot examples
PROMPT-T063 context-window exhaustion attack
PROMPT-T064 prompt pack swap during deployment
PROMPT-T065 model update causes drift
PROMPT-T066 multilingual injection attempt

## 07.07 Acceptance criteria

No prompt pack may be installed without injection, compatibility and regression tests.
Prompt behavior must be attributable to exact prompt + model + context versions.

## 07.08 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
