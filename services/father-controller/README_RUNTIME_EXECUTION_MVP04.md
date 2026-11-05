# FATHER Runtime Execution MVP-04

Purpose: prove that the model selected by the hybrid role router is not only
validated and assembled, but actually executes through UnifiedAgentRuntime.

Checks:
- routine TEXT_ANALYST executes with qwen-analysis-fast / qwen2.5:3b
- complex TEXT_ANALYST executes with qwen-analysis / qwen2.5:7b
- EDGE_FAST executes with llama-small / llama3.2:1b
- runtime response brain_id must match selected brain_id
- non-empty model output is required
- thermal block remains non-bypassable

Run:

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_RUNTIME_EXECUTION_MVP04.ps1
```
