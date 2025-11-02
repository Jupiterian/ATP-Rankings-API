#Find tables with only one row (may cause some issues)
import sqlite3
import os

# Get the project root directory (parent of scripts/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, 'rankings.db')

conn = sqlite3.connect(db_path)
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
