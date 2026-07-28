import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "honeypot.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source_ip TEXT,
            username TEXT,
            password TEXT,
            country TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_attempt(timestamp, source_ip, username, password, country=None, city=None, lat=None, lon=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO attempts (timestamp, source_ip, username, password, country, city, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, source_ip, username, password, country, city, lat, lon))
    conn.commit()
    conn.close()

def get_all_attempts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT timestamp, source_ip, username, password, country, city, latitude, longitude FROM attempts ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
