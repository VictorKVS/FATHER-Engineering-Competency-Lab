# System Analysis
Owner: Senior System Analyst.

Existing packages:
- father-chassis 1.0.0rc1
- father-trust-competency 0.1.0

Requirements:
TI-01 Trust remains separate Python package.
TI-02 chassis declares a dedicated optional integration dependency/profile.
TI-03 local monorepo install is reproducible.
TI-04 CI installs both packages before integration tests.
TI-05 Trust unit tests remain independently runnable.
TI-06 adapter imports only public trust_competency API.
TI-07 no sys.path mutation.
TI-08 no copying Trust source into chassis.
TI-09 compatibility version is explicit.
TI-10 incompatible/missing Trust blocks competency admission fail-closed.

Selected packaging mode for current monorepo:
editable install of sibling project for development/CI, documented as orchestration command, not embedded relative path dependency in wheel metadata.

Future:
published internal package/index can replace editable sibling installation without changing adapter API.