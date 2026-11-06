# NEXUS DEMO AUTOPILOT

Purpose: prove the whole factory line works before enriching every stage.

## Rule

DEMO_AUTOPILOT is an isolated demonstration mode.

For every stage 000-100 it must create:
1. input snapshot
2. input test result
3. minimal specialist artifact
4. artifact test result
5. evidence
6. DEMO_AUTO_APPROVED gate record
7. stage PASS/APPROVED state

## Safety

DEMO_AUTO_APPROVED is never valid as a production human approval.
All evidence produced by this mode is marked DEMO_ONLY.
The run stops immediately on a real filesystem/Git/runtime error.

## Success

The demo is successful only when:
- all 101 stage files exist;
- every stage is APPROVED;
- every stage has PASS input/artifact tests;
- every stage has an evidence file;
- STAGE-100 is APPROVED;
- project.yaml reports DEMO_PRODUCTION_PROVEN;
- the final manifest records 101/101 PASS.
