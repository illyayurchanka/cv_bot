import sqlite3
from pathlib import Path
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id     TEXT UNIQUE NOT NULL,
                username    TEXT,
                first_name  TEXT,
                joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS cvs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id       TEXT NOT NULL,
                file_path     TEXT NOT NULL,
                original_name TEXT,
                version       INTEGER DEFAULT 1,
                is_active     BOOLEAN DEFAULT 1,
                uploaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS cv_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id     TEXT NOT NULL,
                cv_id       INTEGER NOT NULL,
                job_url     TEXT,
                file_path   TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id),
                FOREIGN KEY (cv_id)   REFERENCES cvs(id)
            )
        ''')
