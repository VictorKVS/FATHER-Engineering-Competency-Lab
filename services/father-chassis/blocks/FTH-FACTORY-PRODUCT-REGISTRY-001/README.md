# Product Registry
Block ID: FTH-FACTORY-PRODUCT-REGISTRY-001

Purpose: preserve authoritative product-version identity across factory runs and restarts.

Scope: register/get/list product registrations; idempotent same-recipe registration; fail-closed conflict on same product/version with another recipe_hash; StateStore persistence.

Non-goals: distributed consensus, package storage, signing, release promotion.

Dependencies: ProductRecipe/ProductComposer upstream; ProductRuntime/Qualification downstream; StateStore persistence.

Current maturity: B9 QUALIFIED by G7 M2 persistent lifecycle evidence.