# Algorithm Decision
Owner: Senior Algorithm Engineer.

Options:
1. sys.path manipulation — rejected.
2. copy Trust source into chassis — rejected.
3. PEP 508 relative file dependency inside chassis metadata — rejected for portable package metadata.
4. monorepo orchestration installs both editable packages explicitly — selected for current stage.
5. publish father-trust-competency to internal package index — future production option.

Selected sequence:
python -m pip install -e "projects/FATHER-TRUST-COMPETENCY-0001[dev]"
python -m pip install -e "services/father-chassis[dev]"

CI then runs:
- Trust tests in Trust working directory;
- chassis tests in chassis working directory;
- integration tests that import public trust_competency API.

Compatibility:
father-chassis adapter targets Trust public API 0.1.x for current milestone.