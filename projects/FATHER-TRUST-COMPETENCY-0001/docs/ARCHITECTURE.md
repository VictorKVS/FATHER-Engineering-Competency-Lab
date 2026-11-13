# Architecture

## Boundary

```text
                 +-----------------------------+
                 | Trust & Competency Core     |
                 |-----------------------------|
                 | Subject                     |
                 | Claim                       |
                 | Evidence                    |
                 | Contract                    |
                 | Qualification               |
                 | Competency                  |
                 | Provenance                  |
                 +--------------+--------------+
                                |
                 adapters / profiles only
                                |
          +---------------------+---------------------+
          |                                           |
     FATHER Adapter                              Other Systems
     FQDP / G6 / Blocks                          future consumers
```

## Dependency direction

The core must never import FATHER runtime code.

FATHER may import or call this project through an adapter.

This dependency direction is mandatory for future extraction.

## First real proof case

FATHER Chassis G6 Industrial qualification will become the first PRODUCT competency dataset:

```text
subject: FATHER_CHASSIS
claim: industrially qualified
evidence:
  G6.1
  G6.2
  G6.3
  G6.4
  G6.5
  G6.6
qualification:
  PASS_G6_INDUSTRIAL
```

The same model will later be used for PERSON competency evidence.
