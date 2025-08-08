import sqlite3

conn = sqlite3.connect("files.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    share_code TEXT UNIQUE,
    file_name TEXT,
    file_size INTEGER,
    file_path TEXT,
    uploader_id INTEGER,
    upload_date TEXT
)
""")
conn.commit()
conn.close()
print("Database ready!")
