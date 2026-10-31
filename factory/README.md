# FATHER Factory v0.1

Status: **BOOTSTRAP / EXECUTABLE SKELETON**

Factory turns an approved product specification into a reproducible assembly plan.

## Production line

```text
REQUIREMENTS
  -> CAPABILITIES
  -> CHASSIS
  -> BLOCK MATCHER
  -> REUSE / ADAPT / BUILD
  -> CONFIGURATION
  -> ASSEMBLY MANIFEST
  -> TEST
  -> SECURITY
  -> EVIDENCE
  -> RELEASE
```

## v0.1 objective

Prove one minimal product end-to-end without inventing a new architecture for each project.

The first chassis is `C1_LIGHT_AGENT`. The first product is `HELLO_FACTORY`.

## Block contract

Every reusable block must declare at least:

- id
- version
- type
- inputs
- outputs
- dependencies
- permissions
- security_profile
- tests
- evidence
- compatibility

This is the minimum mechanical "mounting interface" for the Factory.

## Run

```powershell
python factory/runtime/factory.py factory/products/hello_factory.json
python -m unittest factory.tests.test_factory -v
```

## Definition of Done for v0.1

v0.1 is ready only when:

1. product configuration is machine-readable;
2. chassis is selected explicitly;
3. required blocks are resolved from the registry;
4. missing blocks fail the build;
5. an assembly manifest is generated;
6. automated tests pass;
7. evidence records identify what was assembled and from which versions.

No component is considered ready merely because it exists in the repository.
