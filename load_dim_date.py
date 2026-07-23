import os
import pandas as pd
import psycopg2

conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_date (
        full_date DATE PRIMARY KEY,
        year INTEGER NOT NULL,
        quarter INTEGER NOT NULL,
        month INTEGER NOT NULL,
        day_of_week TEXT NOT NULL,
        is_weekday BOOLEAN NOT NULL
    );
""")
conn.commit()
print("dim_date table created (or already existed)")

holdings = pd.read_csv("raw_13f_holdings.csv", parse_dates=["filing_date"])
prices = pd.read_csv("benchmark_prices.csv", parse_dates=["date"])

overall_min = min(holdings["filing_date"].min(), prices["date"].min())
overall_max = max(holdings["filing_date"].max(), prices["date"].max())

print(f"Generating dim_date from {overall_min.date()} to {overall_max.date()}")

all_dates = pd.date_range(start=overall_min, end=overall_max, freq="D")

for d in all_dates:
    cur.execute("""
        INSERT INTO dim_date (full_date, year, quarter, month, day_of_week, is_weekday)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (full_date) DO NOTHING;
    """, (d.date(), d.year, (d.month - 1) // 3 + 1, d.month, d.strftime("%A"), d.weekday() < 5))

conn.commit()

cur.execute("SELECT COUNT(*) FROM dim_date;")
print(f"Total rows in dim_date: {cur.fetchone()[0]}")
cur.execute("SELECT * FROM dim_date ORDER BY full_date LIMIT 5;")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
