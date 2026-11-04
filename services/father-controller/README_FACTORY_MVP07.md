# FATHER Factory MVP-07 — Design Studio UI

First usable visual engineering workspace over the proven FATHER factory backend.

Layout:
- left: live Agent Zoo / Block Registry catalog
- center: visual design canvas with drag/drop nodes and graph edges
- right: inspector and compatibility results
- top: Reference Design, Validate, Auto Complete
- bottom: DESIGN -> BUILD -> BENCH -> RELEASE pipeline indicator

Backend APIs:
- GET /api/health
- GET /api/catalog
- GET /api/project/reference
- POST /api/validate-design
- POST /api/auto-assemble

Run:
    .\START_FATHER_DESIGN_STUDIO.ps1

This is the MVP visual layer. It intentionally reuses the existing Product Spec,
Agent Zoo, Block Registry and Auto Assembly contracts instead of inventing a second architecture.
