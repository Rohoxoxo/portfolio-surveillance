import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS fact_narrative (
        narrative_id SERIAL PRIMARY KEY,
        manager_id INTEGER NOT NULL REFERENCES dim_manager(manager_id),
        year INTEGER NOT NULL,
        quarter INTEGER NOT NULL,
        narrative TEXT,
        UNIQUE (manager_id, year, quarter)
    );
""")
conn.commit()
print("fact_narrative table created (or already existed)")

cur.execute("SELECT manager_id, manager_name FROM dim_manager;")
manager_lookup = {name: mid for mid, name in cur.fetchall()}

narratives = pd.read_csv("fact_narrative.csv")

rows = []
skipped = 0
for _, row in narratives.iterrows():
    manager_id = manager_lookup.get(row["manager_name"])
    if manager_id is None:
        skipped += 1
        print(f"WARNING: no matching manager for '{row['manager_name']}'")
        continue
    rows.append((manager_id, row["year"], row["quarter"], row["narrative"]))

execute_values(cur, """
    INSERT INTO fact_narrative (manager_id, year, quarter, narrative)
    VALUES %s
    ON CONFLICT (manager_id, year, quarter) DO NOTHING;
""", rows)
conn.commit()

cur.execute("SELECT COUNT(*) FROM fact_narrative;")
print(f"Total rows in fact_narrative: {cur.fetchone()[0]}")
print(f"Rows attempted: {len(rows)}, skipped (no manager match): {skipped}")

cur.close()
conn.close()
