# FTH-BRAIN-STORAGE-SELECTION-001 — Explainable Storage Selection Engine

Selects the **minimal sufficient abstract Storage Profile** for a Brain workload.

## Status

**QUALIFIED by local Windows run.**

Qualification:
- Ruff: PASS
- chassis regression: **208 passed**
- edge profile selection: PASS
- hard resource/security constraints: PASS
- minimal-sufficient selection: PASS
- rejected-alternative explanations: PASS
- ambiguity handling: PASS
- deterministic identity: PASS

Canonical evidence:
`artifacts/canonical/QUALIFICATION_EVIDENCE.json`

## Important rule

This block does **not** claim that one database vendor is faster or better than another without benchmark evidence.

It selects an abstract capability profile from declared workload requirements and measured/qualified profile envelopes.

Concrete vendors are bound later through qualified adapters and benchmark evidence.

## Output

The decision contains:
- selected profile;
- reasons for selection;
- rejected alternatives with explicit reasons;
- deterministic decision identity;
- policy/version binding.

## Why

An architect/operator must be able to answer:

> Why B1/EDGE-LITE here, why not B2/B3, and what evidence would change this decision?
