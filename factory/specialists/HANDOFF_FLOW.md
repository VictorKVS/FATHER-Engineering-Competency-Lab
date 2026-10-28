# FATHER Specialist Handoff Flow

Customer / Intent
→ Business Analyst
→ System Analyst
→ Architect
→ Data & Knowledge Engineer
→ AI / LLM Architect
→ Security Specialist
→ Programmer
→ Test Engineer
→ QA / Evals
→ DevSecOps / TIMA
→ Optimization / Experiment
→ RC Freeze
→ Polygon
→ Acceptance / Release

## API rule

Every arrow is an explicit contract.

SPECIALIST A
→ validates OUTPUT_CONTRACT
→ packages API_HANDOFF
→ signs/version-marks artifact
→ sends via REST/Event/GitHub artifact
→ SPECIALIST B validates INPUT_CONTRACT
→ accepts or rejects handoff

## Reject path
If the receiving specialist cannot validate the package:

REJECT
→ reason code
→ failed field/reference
→ evidence
→ return_to_specialist
→ corrected version
→ re-submit

## Example

Business Analyst
POST /handoffs

payload:
- business_model
- requirements
- process flows
- acceptance criteria
- risks
- unresolved questions

System Analyst receives only if:
- schema valid
- critical ambiguities = 0
- G1 passed
- required evidence attached
