import psycopg2

conn = psycopg2.connect("postgresql://postgres:RohitSupabase@db.elkiflvreerejljxclvw.supabase.co:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())
conn.close()
