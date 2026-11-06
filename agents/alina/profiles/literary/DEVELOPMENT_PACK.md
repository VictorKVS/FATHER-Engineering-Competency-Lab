# ALINA Literary — FATHER_CODEX Development Pack

## Goal
Rewrite the literary/story capability as an ALINA specialization under FATHER standards, not as a separate standalone agent.

## Source lineage to preserve
The previous literary line already established these domain concepts:
- CharacterCard
- LocationCard
- SceneCard
- StoryEvent
- RelationshipState
- CanonState
- continuity/state engine
- provenance
- character/object/injury/commitment/goal ledgers
- story graph
- character knowledge boundaries
- canon vs proposal separation

These concepts are requirements inputs. They must be reimplemented only after contract/algorithm review.

## FATHER_CODEX rule
`Requirement -> Algorithm -> Architecture -> Interface Contract -> Security/Policy -> Implementation -> Tests -> Evidence`

Code must not be written from memory if an old implementation can be recovered and reviewed.

Reuse priority:
`REUSE -> WRAP -> ADAPT -> BUILD`

## Target architecture
`AG-001 ALINA CORE + LITERARY PROFILE + STORY DOMAIN MODEL + RAG + KB + MODEL SLOT + EVALS + EVIDENCE`

## Non-goals
- no separate Story Agent identity;
- no hidden conversational memory;
- no model-specific business logic;
- no direct dependency of story domain rules on one LLM vendor;
- no silent mutation of canon.

## Migration strategy
1. freeze literary requirements;
2. recover old code/artifacts where available;
3. classify each artifact REUSE/WRAP/ADAPT/BUILD/REJECT;
4. define domain contracts;
5. implement minimal vertical slice;
6. run continuity tests;
7. bind replaceable model slot;
8. compare models with same contract;
9. add graph/ledgers incrementally;
10. preserve evidence for each migration decision.
