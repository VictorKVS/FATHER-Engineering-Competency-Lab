# Business Process
Owner: Senior Business Analyst.

Goal: every produced product version has one stable, auditable recipe identity that survives restart.

Actors: Product Composer, Product Runtime, Qualification Auditor, DevSecOps.

Input: approved ProductRecipe.
Output: ProductRegistration.

Before: identity could exist only in process memory.
After: registration persists through StateStore and is restored by product_id + version.

KPIs:
- conflicting recipe rejected: 100%;
- restore after reopen: 100%;
- identical recipe registration idempotent: 100%.

Constraint: no implicit overwrite of product identity.