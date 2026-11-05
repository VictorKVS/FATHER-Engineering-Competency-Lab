# FATHER Text Analyst Qualification Bench MVP-01

Purpose: qualification round before the full 163-question exam.

Default matrix:
- every ingested book;
- 30 deterministic diagnostic questions;
- every model reported by local Ollama;
- same lexical retrieval and same top-k context for every model.

Outputs:
- qualification_partial.json (updated during the run)
- qualification_latest.json
- qualification_comparison.json

The comparison file is intentionally technical/reliability-only.
Semantic quality is marked PENDING_REVIEW. Latency alone never crowns a champion.

Run:

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_TEXT_ANALYST_QUALIFICATION.ps1
```

For a smoke test first:

```powershell
python .\run_text_analyst_qualification.py --questions 5 --max-books 1 --models qwen2.5:7b
```

After physical proof:
1. review/evaluate semantic answers;
2. calculate per-dimension scores;
3. select top 3;
4. run full 163-question final.
