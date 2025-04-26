import sqlite3

conn = sqlite3.connect('eco_data.db')
c = conn.cursor()

try:
    c.execute("ALTER TABLE quiz_responses ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP")
    print("✅ 'timestamp' column added successfully.")
except sqlite3.OperationalError as e:
    print("⚠️ Error occurred:", e)

conn.commit()
conn.close()
