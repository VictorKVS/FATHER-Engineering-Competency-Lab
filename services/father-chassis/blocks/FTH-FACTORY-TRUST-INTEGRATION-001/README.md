# Trust Integration Package Contract
Block ID: FTH-FACTORY-TRUST-INTEGRATION-001

Purpose: provide a reproducible, versioned integration boundary between father-chassis and the standalone father-trust-competency package.

Scope:
- package identity/version/API compatibility;
- local monorepo development installation;
- CI installation and independent Trust tests;
- adapter import boundary;
- upgrade/rollback compatibility.

Non-goals:
- merging Trust into chassis;
- duplicating Trust models/evaluator;
- publishing to PyPI in this milestone.

Dependency direction:
father-chassis -> father-trust-competency
father-trust-competency -X-> father-chassis.