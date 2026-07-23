import os
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values

holdings = pd.read_csv("raw_13f_holdings.csv", dtype={"manager_cik": str}, parse_dates=["filing_date"])

# Recompute HHI per manager per quarter, same formula as the DAX measure
def compute_hhi(group):
    total = group["value"].sum()
    weights = group["value"] / total
    return (weights ** 2).sum()

hhi_by_quarter = holdings.groupby(["manager_cik", "manager_name", "filing_date"]).apply(compute_hhi).reset_index(name="hhi")
hhi_by_quarter = hhi_by_quarter.sort_values(["manager_cik", "filing_date"])

forecasts = []

for cik, group in hhi_by_quarter.groupby("manager_cik"):
    group = group.sort_values("filing_date").reset_index(drop=True)
    manager_name = group["manager_name"].iloc[0]

    if len(group) < 2:
        print(f"Skipping {manager_name}: not enough quarters to fit a trend")
        continue

    x = np.arange(len(group))
    y = group["hhi"].values

    slope, intercept = np.polyfit(x, y, deg=1)

    next_x = len(group)
    forecasted_hhi = slope * next_x + intercept

    last_date = group["filing_date"].iloc[-1]
    forecast_date = last_date + pd.Timedelta(days=91)

    forecasts.append({
        "manager_cik": cik,
        "manager_name": manager_name,
        "forecast_date": forecast_date.date(),
        "forecasted_hhi": forecasted_hhi,
        "trend_slope": slope,
        "quarters_used": len(group),
    })

    print(f"{manager_name}: {len(group)} quarters, slope={slope:.4f}, forecast={forecasted_hhi:.4f}")

forecast_df = pd.DataFrame(forecasts)
forecast_df.to_csv("fact_forecast.csv", index=False)
print(f"\nSaved {len(forecast_df)} forecasts to fact_forecast.csv")
