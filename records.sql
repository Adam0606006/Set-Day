CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    mood INTEGER,
    work_hours REAL,
    sleep_hours REAL,
    comment TEXT
);