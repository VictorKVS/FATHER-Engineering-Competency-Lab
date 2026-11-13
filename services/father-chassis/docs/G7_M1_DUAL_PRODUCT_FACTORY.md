# FATHER Factory M1 — Dual Product Qualification

## Goal

Prove repeatable manufacturing rather than a single successful product.

M1 passes only when one FATHER chassis and one factory implementation can:

1. compose two different product specifications;
2. produce different product recipes and assembly hashes;
3. execute both products on the common chassis;
4. collect evidence-bearing traces;
5. produce qualified runtime records;
6. enforce a mandatory human approval contract for the Security/KII product;
7. link product-run evidence into a verified Trust hash-chain.

## Reference products

### Product A — OSINT Knowledge Analyst

- Product ID: `FTH-PRODUCT-OSINT-KNOWLEDGE-001`
- Domain Pack: `DP-OSINT-001`

### Product B — Security & KII Analyst

- Product ID: `FTH-PRODUCT-SECURITY-KII-001`
- Domain Pack: `DP-SECURITY-KII-001`
- Mandatory `create_report` human approval

## M1 acceptance

```text
full chassis regression     PASS
Trust regression            PASS
two distinct products       PASS
different recipe hashes     PASS
different assembly hashes   PASS
OSINT runtime qualification PASS
KII approval stop           PASS
KII approved continuation   PASS
KII runtime qualification   PASS
Trust ledger verification   PASS
```

M1 does not claim final G7 factory qualification. Docker deployments, persistent product registry, persistent approval storage, external provenance signatures, dependency chaos and full product lifecycle qualification remain later gates.
