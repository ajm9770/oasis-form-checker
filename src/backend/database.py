# Use MongoDB or SQLite for metadata tracking
import sqlite3

conn = sqlite3.connect('patient_records.db')
cursor = conn.cursor()

# Create table
cursor.execute('''CREATE TABLE IF NOT EXISTS patients
               (id TEXT PRIMARY KEY,
                transcript_path TEXT,
                history_path TEXT,
                created_at TIMESTAMP)''')
conn.commit()