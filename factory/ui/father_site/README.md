# FATHER Engineering Workspace — Field 01: Agent Designer

First real website workspace for FATHER.

## Scope

Only one field is active in MVP:
**01 — Agent Designer**.

The field visualizes the canonical executable agent formula:

`INPUT + ROLE + PROMPT + RAG + KB + MODEL SLOT + OUTPUT CONTRACT + EVAL + EVIDENCE`

The embedded demo is `AG-001 ALINA / LITERARY`.

## Run locally

From repository root:

```powershell
python -m http.server 8090 --directory factory/ui/father_site
```

Open `http://127.0.0.1:8090`.

## Important

This is a static engineering workspace prototype. "DESIGN PASS" means the design package is structurally complete; it is not equivalent to runtime or Polygon PASS.
