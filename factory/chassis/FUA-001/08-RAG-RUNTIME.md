# FUA-001 / 08.RAG Runtime — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 08.01 Purpose

Retrieve relevant evidence from governed sources while preserving provenance, trust labels and resistance to poisoning/injection.

## 08.02 Required fields

08.01 Source Registry
08.02 Parser
08.03 Chunker
08.04 Metadata
08.05 Embedding
08.06 Index
08.07 Retriever
08.08 Hybrid Search
08.09 Reranker
08.10 Context Builder
08.11 Citation Engine
08.12 Retrieval Evaluator
08.13 Poisoning Detection
08.14 RAG Evidence

## 08.03 Contract

Inputs:
- source registry
- query
- policy context
- trust/classification filters
- retrieval profile

Outputs:
- ranked evidence candidates
- source locators
- trust/provenance metadata
- context package
- retrieval evidence

Invariants:
- every retrieved item has provenance;
- retrieved text is data, not authority;
- source classification is enforced;
- poisoning indicators are preserved;
- citations resolve to exact source locators;
- no retrieval result can silently mutate Role/Policy/Identity.

## 08.04 Initial threats

T01 poisoned source
T02 malicious chunk instruction
T03 source spoofing
T04 metadata tampering
T05 citation mismatch
T06 retrieval manipulation
T07 ranking attack
T08 stale/revoked source
T09 cross-scope data leakage
T10 embedding/index poisoning
T11 malicious document overriding system prompt
T12 untrusted source promoted to trusted context

## 08.05 Draft controls

C01 governed source registry
C02 source hash/provenance
C03 trust labels
C04 parser sanitization
C05 metadata schema
C06 index versioning
C07 query filters
C08 rerank constraints
C09 context source boundaries
C10 citation resolver
C11 poison flags/quarantine
C12 revoked-source filter
C13 retrieval audit
C14 evaluation metrics

## 08.06 Draft test block

### Functional
RAG-T001 register trusted source
RAG-T002 retrieve matching evidence
RAG-T003 return source locator
RAG-T004 preserve metadata
RAG-T005 build bounded context

### Contract
RAG-T010 source without provenance rejected
RAG-T011 invalid locator rejected
RAG-T012 unknown classification rejected
RAG-T013 missing source hash rejected
RAG-T014 malformed chunk metadata rejected

### Security
RAG-T020 malicious instruction remains data
RAG-T021 poisoned source quarantined
RAG-T022 revoked source excluded
RAG-T023 cross-scope source denied
RAG-T024 source metadata tampering detected
RAG-T025 citation cannot resolve to different source
RAG-T026 untrusted source cannot elevate trust
RAG-T027 retrieved content cannot alter Role/Policy
RAG-T028 index poisoning indicator raises event

### Quality
RAG-T030 top-k relevance benchmark
RAG-T031 citation precision
RAG-T032 source coverage
RAG-T033 stale-source detection
RAG-T034 duplicate chunk handling

### Integration
RAG-T040 Prompt Runtime receives trust-labeled context
RAG-T041 Knowledge Runtime distinguishes source evidence from canonical knowledge
RAG-T042 Policy Engine filters restricted sources
RAG-T043 Evaluator scores groundedness
RAG-T044 Audit records query/source set
RAG-T045 Evidence Manager stores retrieval evidence

### POLYGON draft
RAG-T060 adversarial PDF prompt injection
RAG-T061 conflicting trusted/untrusted sources
RAG-T062 poisoned high-rank chunk
RAG-T063 revoked source still present in index
RAG-T064 multilingual injection
RAG-T065 source hash changed after indexing

## 08.07 Acceptance criteria

No retrieved context may be used without provenance/trust metadata.
Poisoning, citation and cross-scope tests are mandatory.

## 08.08 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
