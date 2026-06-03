import sqlite3
from datetime import date

DB_NAME = "database.db"


def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                mood INTEGER,
                work_hours REAL,
                sleep_hours REAL,
                comment TEXT
            )
        """)
        conn.commit()


def add_record(uid, day, mood, work, sleep, comment):
    with connect() as conn:
        conn.execute("""
            INSERT INTO records (
                user_id,
                date,
                mood,
                work_hours,
                sleep_hours,
                comment
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (uid, day, mood, work, sleep, comment))
        conn.commit()


def has_today_record(uid):
    today = date.today().isoformat()

    with connect() as conn:
        cursor = conn.execute("""
            SELECT COUNT(*)
            FROM records
            WHERE user_id = ? AND date = ?
        """, (uid, today))

        return cursor.fetchone()[0] > 0


def get_records(uid, days):
    with connect() as conn:
        cursor = conn.execute("""
            SELECT *
            FROM records
            WHERE user_id = ?
            ORDER BY date
        """, (uid,))

        columns = [col[0] for col in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def clear_data(uid):
    with connect() as conn:
        conn.execute("""
            DELETE FROM records
            WHERE user_id = ?
        """, (uid,))
        conn.commit()

def clear_data(uid):
    with connect() as conn:
        conn.execute("""
            DELETE FROM records
            WHERE user_id = ?
        """, (uid,))
        conn.commit()


def load_test_data():
    with connect() as conn:
        with open("test.sql", "r", encoding="utf-8") as file:
            conn.executescript(file.read())
        conn.commit()
