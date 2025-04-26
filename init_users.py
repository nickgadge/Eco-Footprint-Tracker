import sqlite3

conn = sqlite3.connect('eco_data.db')
c = conn.cursor()

# Create users table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Add user_id to quiz_responses table
c.execute('ALTER TABLE quiz_responses ADD COLUMN user_id INTEGER')

conn.commit()
conn.close()
print("✅ Users table and user_id column added.")
