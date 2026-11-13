# FATHER Factory — Block Roadmap and Required Artifacts

This is the operational backlog for the remaining factory work.

| Block | Current state | Next required artifact | Main owner | Required KB | Qualification focus |
|---|---|---|---|---|---|
| Engineering Workflow Orchestrator | B9 QUALIFIED by M3 | typed artifact schemas + schema migration contract | Architect / System Analyst | KB-ARCHITECTURE, KB-SYSTEM-ANALYSIS | restart, stage order, no skip, tamper detect |
| Stage Artifact Registry | foundation | typed schemas + provenance contract | System Analyst | KB-SYSTEM-ANALYSIS | schema integrity, hash integrity |
| Typed Stage Artifacts | B9 QUALIFIED by M4 | migration adapters + signed schema releases (future) | System Analyst / Architect | KB-SYSTEM-ANALYSIS, KB-ARCHITECTURE | type safety, schema versioning, persistence roundtrip |
| Trust Integration | B9 QUALIFIED by M5A | immutable package/signing/internal index (future) | DevSecOps / Trust Architect | KB-DEVSECOPS, KB-QUALIFICATION-EVIDENCE | reproducible package boundary |
| Competency Admission | B9 QUALIFIED by M5 | persistent Trust source + policy calibration (future) | Trust Architect | KB-QUALIFICATION-EVIDENCE | wrong competency blocked |
| Qualified KB Admission | B6 pre-code document pack | implementation + G7 M6 evidence | Knowledge Architect | KB-QUALIFICATION-EVIDENCE | unqualified KB blocked |
| Knowledge Source Intake | planned | business process + source contract | Business/System Analyst | KB-SYSTEM-ANALYSIS | source accepted/rejected correctly |
| Rights/Access/Legal Check | planned | decision algorithm + evidence contract | Security/Legal adapter | KB-QUALIFICATION-EVIDENCE | illegal/unknown source blocked |
| Fingerprint/Dedup | planned | algorithm benchmark | Algorithm Engineer | KB-ALGORITHMS | deterministic dedup |
| Metadata/Provenance | partial | typed schema + lifecycle | System Analyst | KB-SYSTEM-ANALYSIS | required metadata complete |
| Parser/Extractor | planned | algorithm decision | Algorithm Engineer | KB-ALGORITHMS | extraction fidelity |
| Chunker | planned | benchmark matrix | Algorithm Engineer | KB-ALGORITHMS | retrieval quality/cost |
| Entity/Relation Extraction | planned | ontology + algorithm decision | Knowledge Architect | KB-ALGORITHMS, KB-ARCHITECTURE | entity precision/recall |
| Normalizer | planned | canonical model | System Analyst | KB-SYSTEM-ANALYSIS | semantic consistency |
| Knowledge Graph | partial concept | graph architecture | Architect | KB-ARCHITECTURE | referential integrity |
| Conflict/Version Resolver | planned | resolution algorithm | Algorithm Engineer | KB-ALGORITHMS | conflict determinism |
| Index Builder | planned | vector/lexical/hybrid decision | Algorithm Engineer | KB-ALGORITHMS | recall/latency/cost |
| Retrieval Evaluator | planned | metric/test contract | Test Architect | KB-TEST-ENGINEERING | recall/precision/grounding |
| KB Release Manager | planned | release lifecycle | DevSecOps / Knowledge Architect | KB-DEVSECOPS | reproducibility/versioning |
| Requirement Planner | implemented foundation | formal block doc pack | System Analyst | KB-SYSTEM-ANALYSIS | requirement coverage |
| Capability Model | implemented foundation | formal semantics | Architect | KB-ARCHITECTURE | completeness |
| Block Catalog | implemented | persistence/version contract | Architect | KB-ARCHITECTURE | compatibility |
| Block Matcher | implemented | optimization algorithm review | Algorithm Engineer | KB-ALGORITHMS | deterministic/best-fit |
| Domain Pack | foundation | package standard | Architect | KB-ARCHITECTURE | separability |
| Agent Factory | foundation | execution/competency binding | Architect | KB-ARCHITECTURE | correct role/tools/KB |
| Product Recipe | implemented | full document pack | Architect/System Analyst | KB-ARCHITECTURE | deterministic identity |
| Product Composer | implemented | full document pack | Architect | KB-ARCHITECTURE | composition correctness |
| Product Registry | B9 QUALIFIED by M2 | M2 evidence, then concurrency/migration extension | System Analyst | KB-SYSTEM-ANALYSIS | restart/conflict/concurrency |
| Product Builder | planned | build algorithm + manifest schema | Architect/DevOps | KB-DEVSECOPS | reproducible product build |
| Config Generator | planned | schema + merge rules | System Analyst | KB-SYSTEM-ANALYSIS | deterministic config |
| Deployment Manifest Generator | planned | target abstraction | DevSecOps | KB-DEVSECOPS | valid/reproducible deploy |
| Product Runtime | M1 foundation | lifecycle architecture | Architect/SRE | KB-ARCHITECTURE | execution/evidence |
| Product Qualification | foundation | qualification policy | Qualification Auditor | KB-QUALIFICATION-EVIDENCE | independent pass/fail |
| Evidence Ledger | foundation | persistence/signature architecture | Trust Architect | KB-QUALIFICATION-EVIDENCE | append-only/hash chain |
| Provenance Chain | planned | provenance schema | Trust Architect | KB-QUALIFICATION-EVIDENCE | artifact lineage |
| Competency Engine | foundation | admission policy | Trust Architect | KB-QUALIFICATION-EVIDENCE | C-level enforcement |
| UAG Policy Engine | planned/partial concept | action authority model | Security Architect | KB-ARCHITECTURE | reasoning != authority |
| Human Approval Gate | B9 QUALIFIED by M2 | M2 evidence, then approver identity/TTL/revocation design | Security Architect | KB-ARCHITECTURE | fail-closed authority + restart persistence |
| Tool Permission Boundary | foundation | formal permission matrix | Security Architect | KB-ARCHITECTURE | least privilege |
| POLYGON Scenario Catalog | planned | scenario schema | Test Architect | KB-TEST-ENGINEERING | coverage |
| Functional Evaluator | planned | evaluator contract | Test Architect | KB-TEST-ENGINEERING | task correctness |
| Security Evaluator | planned | attack/test model | Security Architect | KB-TEST-ENGINEERING | adversarial resilience |
| Performance Evaluator | planned | SLO/resource model | Test Architect/SRE | KB-TEST-ENGINEERING | latency/throughput/resources |
| Cost Evaluator | planned | cost model | Business/FinOps | KB-BUSINESS-ANALYSIS | cost efficiency |
| Regression Evaluator | planned | baseline/change model | Test Architect | KB-TEST-ENGINEERING | no degradation |
| Build Pipeline | implemented foundation | product-level pipeline | DevSecOps | KB-DEVSECOPS | reproducible build |
| SBOM / Supply Chain | G6 chassis proven | product-level extension | DevSecOps | KB-DEVSECOPS | provenance/vulnerabilities |
| Observability | chassis proven | product-level SLO contracts | SRE | KB-DEVSECOPS | logs/metrics/traces |
| Upgrade/Rollback | chassis proven | product-level lifecycle | SRE | KB-DEVSECOPS | rollback integrity |
| Chaos/Recovery | chassis proven | product-level scenarios | SRE/Test | KB-TEST-ENGINEERING | recovery behavior |
| Enterprise Metamodel | G8 planned | business/system model | Enterprise Architect | KB-ARCHITECTURE | model completeness |
| Capability Map | G8 planned | business architecture contract | Business Architect | KB-BUSINESS-ANALYSIS | goal-capability trace |
| Enterprise Graph/Digital Twin | G8 planned | graph architecture | Enterprise Architect | KB-ARCHITECTURE | current-state fidelity |
| AI Opportunity Engine | G8 planned | scoring algorithm | Algorithm/Business | KB-ALGORITHMS, KB-BUSINESS-ANALYSIS | value/risk/cost ranking |
| Architecture Drift | G8 planned | drift model | Enterprise Architect | KB-ARCHITECTURE | intended vs actual |

## Rule for taking a block into implementation

Before code changes for any row above:

1. create/update the block document directory;
2. complete BUSINESS_PROCESS;
3. complete SYSTEM_ANALYSIS;
4. complete ALGORITHM_DECISION;
5. complete ARCHITECTURE;
6. complete INTERFACES_AND_VARIABLES;
7. complete SECURITY_MODEL;
8. Test Architect creates TEST_CONTRACT;
9. DevelopmentPacket is generated and approved;
10. only then Senior Developer changes code.

## Rule for existing legacy/foundation blocks

Already implemented blocks are not exempt.

They enter a documentation backfill cycle:

```text
existing code
  -> reverse-engineer current contract
  -> business/system review
  -> algorithm review
  -> architecture freeze
  -> test contract
  -> reconcile implementation
  -> qualification
```

If documentation and implementation disagree, implementation is not treated as truth automatically. The discrepancy is escalated to architecture/system analysis.


## Reference block packages

The first complete document-pack baselines are:

- `blocks/FTH-FACTORY-PRODUCT-REGISTRY-001/`
- `blocks/FTH-CORE-APPROVAL-001/`

Both reference blocks are now B9 QUALIFIED by the G7 M2 persistent lifecycle gate. Canonical evidence records the 85-test regression and restart/recovery lifecycle.
