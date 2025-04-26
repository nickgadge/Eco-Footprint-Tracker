import sqlite3

conn = sqlite3.connect('eco_data.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS quiz_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transport TEXT,
        diet TEXT,
        electricity TEXT,
        score INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
print("✅ Database initialized.")
