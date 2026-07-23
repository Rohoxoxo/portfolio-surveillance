import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS fact_forecast (
        forecast_id SERIAL PRIMARY KEY,
        manager_cik TEXT NOT NULL,
        forecast_date DATE NOT NULL,
        forecasted_hhi NUMERIC,
        trend_slope NUMERIC,
        quarters_used INTEGER,
        UNIQUE (manager_cik, forecast_date)
    );
""")
conn.commit()
print("fact_forecast table created (or already existed)")

forecast = pd.read_csv("fact_forecast.csv", dtype={"manager_cik": str}, parse_dates=["forecast_date"])

rows = list(forecast[["manager_cik", "forecast_date", "forecasted_hhi", "trend_slope", "quarters_used"]].itertuples(index=False, name=None))
rows = [(mc, fd.date(), hhi, slope, qu) for mc, fd, hhi, slope, qu in rows]

execute_values(cur, """
    INSERT INTO fact_forecast (manager_cik, forecast_date, forecasted_hhi, trend_slope, quarters_used)
    VALUES %s
    ON CONFLICT (manager_cik, forecast_date) DO NOTHING;
""", rows)
conn.commit()

cur.execute("SELECT COUNT(*) FROM fact_forecast;")
print(f"Total rows in fact_forecast: {cur.fetchone()[0]}")

cur.execute("SELECT * FROM fact_forecast;")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
