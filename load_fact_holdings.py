import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS fact_holdings (
        holding_id SERIAL PRIMARY KEY,
        manager_id INTEGER NOT NULL REFERENCES dim_manager(manager_id),
        security_id INTEGER NOT NULL REFERENCES dim_security(security_id),
        filing_date DATE NOT NULL REFERENCES dim_date(full_date),
        value NUMERIC,
        shares NUMERIC,
        UNIQUE (manager_id, security_id, filing_date)
    );
""")
conn.commit()
print("fact_holdings table created (or already existed)")

cur.execute("SELECT manager_id, manager_cik FROM dim_manager;")
manager_lookup = {cik: mid for mid, cik in cur.fetchall()}

cur.execute("SELECT security_id, cusip FROM dim_security;")
security_lookup = {cusip: sid for sid, cusip in cur.fetchall()}

holdings = pd.read_csv("raw_13f_holdings.csv", dtype={"manager_cik": str}, parse_dates=["filing_date"])

rows_to_insert = []
skipped_no_security = 0

for _, row in holdings.iterrows():
    manager_id = manager_lookup.get(row["manager_cik"])
    security_id = security_lookup.get(row["cusip"])

    if security_id is None:
        skipped_no_security += 1
        continue

    rows_to_insert.append((manager_id, security_id, row["filing_date"].date(), row["value"], row["shares"]))

print(f"Inserting {len(rows_to_insert)} rows in batches...")

execute_values(cur, """
    INSERT INTO fact_holdings (manager_id, security_id, filing_date, value, shares)
    VALUES %s
    ON CONFLICT (manager_id, security_id, filing_date) DO NOTHING;
""", rows_to_insert, page_size=500)

conn.commit()

cur.execute("SELECT COUNT(*) FROM fact_holdings;")
print(f"Total rows in fact_holdings: {cur.fetchone()[0]}")
print(f"Rows attempted: {len(rows_to_insert)}, skipped (security not in dim_security): {skipped_no_security}")

cur.close()
conn.close()
