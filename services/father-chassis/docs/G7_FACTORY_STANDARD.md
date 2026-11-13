# FATHER G7 Factory Standard

## Purpose

G7 turns the already qualified FATHER Chassis into a repeatable product factory.

The factory must not create a product by ad-hoc coding alone. It must transform requirements into explicit capabilities, match reusable blocks, create a product recipe, attach contracts and evidence requirements, assemble on the common chassis, and qualify the result.

## Production line

```text
CUSTOMER REQUIREMENT
    -> REQUIREMENT PLAN
    -> REQUIRED CAPABILITIES
    -> BLOCK CATALOG
    -> BLOCK MATCHER
    -> DOMAIN PACK
    -> PRODUCT RECIPE
    -> AGENT / WORKFLOW COMPOSITION
    -> CHASSIS EXECUTION
    -> TEST / SECURITY / EVIDENCE
    -> PRODUCT QUALIFICATION
```

## Mandatory product contents

Every product recipe must identify:

- product and version;
- originating requirement;
- agent/workflow identity;
- selected reusable block IDs;
- required capabilities;
- optional domain pack;
- five contract classes:
  - component;
  - data;
  - security;
  - qualification;
  - ownership/provenance;
- required evidence.

## Factory rule

A product is not considered ready because a recipe can be generated.

It must pass:

1. recipe validation;
2. unit tests;
3. integration tests;
4. security checks;
5. runtime execution;
6. trace/audit verification;
7. qualification evidence.

## Extraction rule

Products and domain packs must not depend on `services/father-controller`.

The common chassis is a runtime dependency through contracts. Domain logic belongs in separable product/domain-pack boundaries.

## Current G7 implementation state

- G7.0 Factory standard: IMPLEMENTED
- G7.1 Block Catalog: IMPLEMENTED
- G7.2 deterministic Block Matcher: IMPLEMENTED
- G7.3 Product Recipe: IMPLEMENTED
- G7.4 Domain Pack contract: FOUNDATION IMPLEMENTED
- G7.5 Agent Factory: EXISTS, requires G7 qualification alignment
- G7.6 Knowledge Factory: NEXT
- G7.7 Trust/Competency/Provenance integration: NEXT
- G7.8 automatic product assembly: NOT YET QUALIFIED
- G7.9 product runtime qualification: NOT YET RUN
- G7.10 factory qualification: NOT YET RUN
