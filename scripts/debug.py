#Find tables with only one row (may cause some issues)
import sqlite3

conn = sqlite3.connect("rankings.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'temp_%'")
tables = [row[0] for row in cursor.fetchall()]

single_row_tables = []

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM '{table}'")
    count = cursor.fetchone()[0]
    if count == 1:
        single_row_tables.append(table)

print("Tables with only 1 row:", single_row_tables)

conn.close()
