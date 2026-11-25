import duckdb

con = duckdb.connect("olist.duckdb")

for (t,) in con.execute("SHOW TABLES").fetchall():
    print("\n==", t, "==")
    con.sql(f"DESCRIBE {t}").show()