import os
import psycopg2

conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_benchmark (
        benchmark_id SERIAL PRIMARY KEY,
        ticker TEXT UNIQUE NOT NULL,
        benchmark_name TEXT NOT NULL
    );
""")
conn.commit()
print("dim_benchmark table created (or already existed)")

benchmarks = [
    ("SPY", "S&P 500 (Broad Market)"),
    ("XLK", "Technology Sector"),
    ("XLF", "Financials Sector"),
    ("XLE", "Energy Sector"),
]

for ticker, name in benchmarks:
    cur.execute("""
        INSERT INTO dim_benchmark (ticker, benchmark_name)
        VALUES (%s, %s)
        ON CONFLICT (ticker) DO NOTHING;
    """, (ticker, name))

conn.commit()

cur.execute("SELECT * FROM dim_benchmark ORDER BY benchmark_id;")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
