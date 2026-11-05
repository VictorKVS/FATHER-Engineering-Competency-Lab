# FATHER Hybrid Runtime Router MVP-03

This is the first integration layer where the role-based decision is translated
into a real FATHER Brain ID and validated/built through ProductFactory.

Promoted lanes:
- TEXT_ANALYST routine -> qwen-analysis-fast -> qwen2.5:3b
- TEXT_ANALYST complex -> qwen-analysis -> qwen2.5:7b
- EDGE_FAST -> llama-small -> llama3.2:1b

Fallback:
- non-promoted lanes stay on Stage29
- CODING therefore still resolves through Stage29 to qwen-coder
- thermal block is a safety gate and must never fall back around the block

MVP-03 validates real ProductFactory assembly. It does not yet execute a full
LLM inference request in the new lane; runtime execution comes after this
assembly/compatibility acceptance passes locally.

Run:
```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_HYBRID_RUNTIME_ROUTER_MVP03.ps1
```
