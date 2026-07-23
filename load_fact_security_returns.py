import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS fact_security_returns (
        return_id SERIAL PRIMARY KEY,
        ticker TEXT NOT NULL,
        date DATE NOT NULL REFERENCES dim_date(full_date),
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        adj_close NUMERIC,
        volume BIGINT,
        UNIQUE (ticker, date)
    );
""")
conn.commit()
print("fact_security_returns table created (or already existed)")

security_prices = pd.read_csv("security_prices.csv")
benchmark_prices = pd.read_csv("benchmark_prices.csv")

all_prices = pd.concat([security_prices, benchmark_prices], ignore_index=True)
all_prices["date"] = pd.to_datetime(all_prices["date"], format="mixed", utc=True).dt.date
all_prices = all_prices.drop_duplicates(subset=["ticker", "date"])

numeric_cols = ["open", "high", "low", "close", "adj_close", "volume"]
for col in numeric_cols:
    all_prices[col] = all_prices[col].astype(object).where(pd.notnull(all_prices[col]), None)

rows = list(all_prices[["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]].itertuples(index=False, name=None))

print(f"Inserting {len(rows)} rows in chunks...")

CHUNK_SIZE = 50000
for i in range(0, len(rows), CHUNK_SIZE):
    chunk = rows[i:i + CHUNK_SIZE]
    execute_values(cur, """
        INSERT INTO fact_security_returns (ticker, date, open, high, low, close, adj_close, volume)
        VALUES %s
        ON CONFLICT (ticker, date) DO NOTHING;
    """, chunk, page_size=2000)
    conn.commit()
    print(f"Committed {min(i + CHUNK_SIZE, len(rows))} / {len(rows)}")

cur.execute("SELECT COUNT(*) FROM fact_security_returns;")
print(f"\nTotal rows in fact_security_returns: {cur.fetchone()[0]}")

cur.close()
conn.close()
