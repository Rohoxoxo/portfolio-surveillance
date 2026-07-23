import os
import pandas as pd
import psycopg2

conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_manager (
        manager_id SERIAL PRIMARY KEY,
        manager_cik TEXT UNIQUE NOT NULL,
        manager_name TEXT NOT NULL
    );
""")
conn.commit()
print("dim_manager table created (or already existed)")

holdings = pd.read_csv("raw_13f_holdings.csv", dtype={"manager_cik": str})
managers = holdings[["manager_cik", "manager_name"]].drop_duplicates()

for _, row in managers.iterrows():
    cur.execute("""
        INSERT INTO dim_manager (manager_cik, manager_name)
        VALUES (%s, %s)
        ON CONFLICT (manager_cik) DO NOTHING;
    """, (row["manager_cik"], row["manager_name"]))

conn.commit()

cur.execute("SELECT * FROM dim_manager ORDER BY manager_id;")
rows = cur.fetchall()
for r in rows:
    print(r)

cur.close()
conn.close()
