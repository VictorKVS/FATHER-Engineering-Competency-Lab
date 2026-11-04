# FATHER Factory MVP-03 — Design Studio Data Model

This milestone introduces the backend model for the future visual FATHER Design Studio.

A design project contains:
- project identity and chassis
- visual nodes with positions
- graph edges and relations
- Agent references
- Block Registry references
- product defaults

The project can:
1. validate graph integrity,
2. verify referenced reusable blocks,
3. export a Product Spec,
4. feed that Product Spec into Product Factory.

This is intentionally not the frontend yet. It proves the canvas has a stable data model before UI work begins.
