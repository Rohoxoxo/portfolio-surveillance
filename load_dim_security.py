import os
import pandas as pd
import psycopg2

conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_security (
        security_id SERIAL PRIMARY KEY,
        cusip TEXT UNIQUE NOT NULL,
        ticker TEXT NOT NULL,
        company_name TEXT,
        sector TEXT,
        industry TEXT
    );
""")
conn.commit()
print("dim_security table created (or already existed)")

securities = pd.read_csv("cusip_ticker_sector_map.csv")

for _, row in securities.iterrows():
    cur.execute("""
        INSERT INTO dim_security (cusip, ticker, company_name, sector, industry)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (cusip) DO NOTHING;
    """, (row["cusip"], row["ticker"], row["company_name"], row["sector"], row["industry"]))

conn.commit()

cur.execute("SELECT COUNT(*) FROM dim_security;")
print(f"Total rows in dim_security: {cur.fetchone()[0]}")

cur.execute("SELECT * FROM dim_security LIMIT 5;")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
