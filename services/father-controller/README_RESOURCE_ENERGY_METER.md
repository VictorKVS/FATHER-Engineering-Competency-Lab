# FATHER Resource & Energy Meter v1

Measures the cost of local AI work.

## Measured directly
- NVIDIA GPU temperature
- NVIDIA GPU utilization
- NVIDIA GPU power draw
- VRAM use

Source: local `nvidia-smi`.

## Estimated
- CPU package power from CPU utilization (when `psutil` is available)
- rest-of-system baseline
- total system power
- Wh / kWh
- money cost using a user supplied electricity tariff
- average Wh and cost per task

The report keeps measured and estimated values separate.

## Qualification benchmark

```powershell
cd G:\1\FATHER-Engineering-Competency-Lab\services\father-controller
.\RUN_FATHER_TEXT_ANALYST_QUALIFICATION_METERED.ps1 -PricePerKWh 8.50 -Currency RUB
```

Replace 8.50 with the tariff from your electricity bill.

Evidence:
`evidence/resource_energy/resource_energy_*.csv`
`evidence/resource_energy/resource_energy_*.json`

The CSV is the temperature/power time series. JSON is the run summary.
