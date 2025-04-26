import sqlite3

conn = sqlite3.connect('eco_data.db')
c = conn.cursor()

# Step 1: Rename old table
c.execute('ALTER TABLE quiz_responses RENAME TO quiz_responses_old')

# Step 2: Create new table with timestamp column
c.execute('''
    CREATE TABLE quiz_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transport TEXT,
        diet TEXT,
        electricity TEXT,
        score INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Step 3: Copy old data into new table (without timestamp — it will auto-fill)
c.execute('''
    INSERT INTO quiz_responses (transport, diet, electricity, score)
    SELECT transport, diet, electricity, score FROM quiz_responses_old
''')

# Step 4: Drop old table
c.execute('DROP TABLE quiz_responses_old')

conn.commit()
conn.close()
print("✅ Migration complete. Timestamp column added.")
