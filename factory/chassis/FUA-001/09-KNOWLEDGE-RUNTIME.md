# FUA-001 / 09.Knowledge Runtime — Block Design Draft

Status: 03.TESTS_DRAFTED
Version: 0.1

## 09.01 Purpose

Maintain governed canonical knowledge separately from transient memory and raw RAG evidence.

## 09.02 Required fields

09.01 Knowledge Base
09.02 Concept Registry
09.03 Definition Registry
09.04 Ontology
09.05 Knowledge Graph
09.06 Algorithms Registry
09.07 Rules Registry
09.08 Examples / Cases
09.09 Checklists
09.10 Negative Knowledge
09.11 Contradictions
09.12 Provenance
09.13 Confidence
09.14 Knowledge Validation

## 09.03 Invariants

- canonical knowledge requires validation;
- source-derived and ALINA-synthesized definitions remain distinguishable;
- contradiction is preserved, not silently overwritten;
- every knowledge item has provenance, confidence and review status;
- revoked source support must invalidate or downgrade dependent knowledge;
- memory is not canonical knowledge.

## 09.04 Initial threats

T01 false fact promotion
T02 source laundering
T03 contradiction suppression
T04 provenance loss
T05 confidence inflation
T06 unauthorized canonicalization
T07 malicious knowledge update
T08 stale/revoked source dependence
T09 ontology poisoning
T10 cross-domain contamination

## 09.05 Draft controls

C01 typed knowledge records
C02 explicit definition_type
C03 validation gate
C04 source locator set
C05 contradiction registry
C06 review status
C07 immutable revision history
C08 confidence policy
C09 source revocation propagation
C10 policy-controlled canonicalization

## 09.06 Draft tests

KNOW-T001 register candidate knowledge
KNOW-T002 canonicalize reviewed candidate
KNOW-T003 reject canonicalization without provenance
KNOW-T004 preserve conflicting definitions
KNOW-T005 source revocation downgrades dependent item
KNOW-T020 model cannot self-canonicalize
KNOW-T021 memory item is not accepted as canonical without validation
KNOW-T022 confidence cannot exceed policy bounds
KNOW-T030 RAG evidence links to knowledge record
KNOW-T031 Audit records canonicalization decision
KNOW-T032 Evaluator can inspect provenance/confidence

## 09.07 Current decision

BLOCK STATUS: TESTS_DRAFTED
INSTALLATION PERMIT: DENIED
