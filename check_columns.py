import sqlite3

conn = sqlite3.connect('eco_data.db')
c = conn.cursor()

c.execute("PRAGMA table_info(quiz_responses)")
columns = c.fetchall()

for col in columns:
    print(f"Column: {col[1]} | Type: {col[2]}")

conn.close()
