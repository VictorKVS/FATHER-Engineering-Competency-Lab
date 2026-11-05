# FATHER Adaptive Role Router MVP-02

Shadow-mode router built on top of Role Model Matrix MVP-01.

Routing policy:

- routine TEXT_ANALYST -> qwen2.5:3b
- difficult TEXT_ANALYST (complexity 3-4) -> qwen2.5:7b
- EDGE_FAST -> llama3.2:1b
- CREATIVE_WRITING -> blocked for production until creative semantic bench;
  experimental multi-draft can return Ministral + Qwen 7B + Qwen 3B
- CODING / REASONING / VISION remain controlled by their role-specific bench status
- GPU at or above project thermal review gate -> route blocked until cooldown

This is deliberately SHADOW mode. It proves decisions without replacing Stage29.

Run:

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_ADAPTIVE_ROLE_ROUTER_MVP02.ps1
```

Expected checks:
- routine_text_analysis_uses_qwen3b
- complex_text_analysis_escalates_qwen7b
- creative_multidraft_keeps_three_writers
- creative_production_still_blocked_before_bench
- thermal_gate_blocks_hot_gpu
- simple_task_uses_edge_fast
