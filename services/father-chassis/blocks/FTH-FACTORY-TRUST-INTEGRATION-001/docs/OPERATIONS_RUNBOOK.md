# Operations Runbook
Owner: DevSecOps/SRE.

Local setup from repository root:
python -m pip install -e "projects/FATHER-TRUST-COMPETENCY-0001[dev]"
python -m pip install -e "services/father-chassis[dev]"

Health:
python -c "import trust_competency; print(trust_competency.CompetencyEvaluator)"

Upgrade:
run Trust tests, API compatibility tests, chassis regression, competency admission qualification.

Rollback:
restore previous compatible Trust package and chassis adapter together.

Production future:
replace editable install with immutable signed package artifact.