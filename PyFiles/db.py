import sqlite3
from datetime import datetime, timedelta
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "table.db")
SQL_DIR = os.path.join(os.path.dirname(BASE_DIR), "DbFiles")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    for f in ["users.sql", "records.sql"]:
        path = os.path.join(SQL_DIR, f)
        if os.path.exists(path):
            with open(path) as file:
                conn.executescript(file.read())
    conn.commit()
    conn.close()

def add_user(tid, name):
    conn = get_conn()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT OR IGNORE INTO users (telegram_id, username, created_at) VALUES (?, ?, ?)", (tid, name, now))
    conn.commit()
    conn.close()

def add_record(uid, dt, mood, work, sleep, comment):
    conn = get_conn()
    conn.execute("INSERT INTO records (user_id, date, mood, work_hours, sleep_hours, comment) VALUES (?, ?, ?, ?, ?, ?)", (uid, dt, mood, work, sleep, comment))
    conn.commit()
    conn.close()

def get_records(uid, days):
    conn = get_conn()
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cursor = conn.execute("SELECT * FROM records WHERE user_id = ? AND date >= ? ORDER BY date", (uid, start))
    res = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return res

def clear_data(uid):
    conn = get_conn()
    conn.execute("DELETE FROM records WHERE user_id = ?", (uid,))
    conn.commit()
    conn.close()

def has_today_record(uid):
    conn = get_conn()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor = conn.execute("SELECT COUNT(*) FROM records WHERE user_id = ? AND date = ?", (uid, today))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0
