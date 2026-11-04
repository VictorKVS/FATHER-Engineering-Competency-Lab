# FATHER Factory MVP-02 — Block Contract

Purpose: make every reusable FATHER component describable in one Design Studio-compatible schema.

Block Contract v1 includes:
- id / type / version / lifecycle status
- capabilities
- inputs / outputs
- dependencies
- resource class
- permissions
- security metadata
- tests
- compatibility metadata

Runtime-specific fields remain extensible.

This milestone does not claim every block is production-approved.
It proves the registry can represent blocks uniformly, discover them by capability,
validate existing products, and reject missing components.
