# FATHER Semantic Escalation Runtime MVP-07

Production path:
3B execution -> semantic claim gate -> accept OR escalate to 7B -> semantic gate again.

Important:
- Production code has no forced reject.
- The test harness uses one explicit fault-injection subclass only to prove the escalation control flow deterministically.
- Real execution and real semantic checking are still performed on both model attempts.
- Thermal blocking remains upstream of execution and semantic evaluation.

Run:
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_SEMANTIC_ESCALATION_MVP07.ps1
