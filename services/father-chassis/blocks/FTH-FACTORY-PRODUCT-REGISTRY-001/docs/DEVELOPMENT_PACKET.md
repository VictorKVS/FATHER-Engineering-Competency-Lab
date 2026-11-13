# Development Packet
Owner: Engineering Orchestrator.
Status: APPROVED FOR CURRENT M2 BASELINE.

Immutable semantics:
- key = product_id@version;
- same key cannot map to different recipe_hash;
- persistence namespace = product_registry;
- cache must not override durable conflict semantics;
- no father-controller dependency.

Implementation: src/father/factory/product_registry.py
Tests: tests/test_product_registry.py; tests/test_factory_persistence.py

Changes to key semantics, conflict behavior, persistence schema or lifecycle require upstream Business/System/Algorithm/Architecture/Test review.