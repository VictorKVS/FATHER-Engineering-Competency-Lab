# FATHER Chassis v1.8 / Stage 9

Stage 9 introduces the Agent Zoo.

It proves that multiple agents can be assembled from the same AgentChassis using manifests only.

Registered profiles:

- father-general-agent -> qwen-analysis + generic
- father-ib-agent -> qwen-analysis + ib_demo
- father-edge-agent -> llama-small + generic
- father-coder-agent -> qwen-coder + generic
- father-lab-agent -> existing laboratory profile

Release checks:

- Agent Zoo registry health
- required manifests registered
- every manifest assembles
- role profiles execute through one chassis contract
- knowledge delivery is present
- deterministic task quality passes
- all agents expose the same run/swap_brain/apply_competency/call_tool contract

Run:

    cd G:\1\FATHER-Engineering-Competency-Lab
    .\FATHER_UPDATE.ps1

Expected:

    RUNNER: RUN_FATHER_STAGE9.ps1
