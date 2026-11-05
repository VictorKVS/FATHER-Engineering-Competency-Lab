# FATHER Text Analyst Value Bench MVP-01

Purpose: compare approved text-analysis candidates on the same workload using:

- quality from the completed Quality Judge;
- latency from a fresh identical workload;
- GPU temperature and GPU watts from `nvidia-smi`;
- estimated total system energy;
- Wh/task;
- optional electricity cost/task.

Candidates:
- qwen2.5:3b
- qwen2.5:7b
- qwen2.5-coder:7b-instruct-q4_K_M
- llama3.2:1b

Final score:

`VALUE = 0.60 * QUALITY + 0.20 * SPEED + 0.20 * ECONOMY`

Run:

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_TEXT_ANALYST_VALUE_BENCH.ps1 -PricePerKWh 0 -Currency RUB
```

Replace 0 with the actual electricity tariff when known.

Evidence:
- `evidence/resource_energy/resource_energy_*_<model>.json`
- `evidence/resource_energy/resource_energy_*_<model>.csv`
- `evidence/text_analyst_value/value_workload_<model>.json`
- `evidence/text_analyst_value/value_matrix_latest.json`
