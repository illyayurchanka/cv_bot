import sqlite3
from pathlib import Path
from config import DB_PATH, CV_DIR

class DATABASE:
    @staticmethod
    def init_db():
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                    CREATE TABLE IF NOT EXISTS users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id TEXT UNIQUE NOT NULL,
                        username TEXT,
                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        cv_exist INTEGER DEFAULT 0
                    )
            ''')

            conn.execute('''
                    CREATE TABLE IF NOT EXISTS cv_history(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id TEXT NOT NULL,
                        job_url TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
            ''')

    @staticmethod
    def save_user(chat_id: str, username: str):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)', (chat_id, username))

    @staticmethod
    def get_user(chat_id: str) -> sqlite3.Row | None:
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,)).fetchone()
            return row

    @staticmethod
    def save_cv(chat_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('UPDATE users SET cv_exist = 1 WHERE chat_id = ?', (chat_id,))

    @staticmethod
    def get_cv_status(chat_id):
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,)).fetchone()
            return row[-1]

    @staticmethod 
    def save_cv_history(chat_id, job_url):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute('INSERT INTO cv_history (chat_id, job_url) VALUES (?, ?)', (chat_id, job_url))
            return cursor.lastrowid

    @staticmethod
    def get_cv_history(chat_id):
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute('SELECT * FROM cv_history WHERE chat_id = ?', (chat_id,)).fetchall()
            return rows

    @staticmethod
    def get_cv_path(chat_id: str) -> Path:
        user_dir = CV_DIR / chat_id

        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir/ 'cv.tex'

    @staticmethod
    def save_cv_file(chat_id: str, file_bytes: bytes):
        file_path = DATABASE.get_cv_path(chat_id)
        output_dir = CV_DIR / chat_id / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        print("saving file")
        file_path.write_bytes(file_bytes)
        DATABASE.save_cv(chat_id)
        print("file saved")

    @staticmethod
    def get_pdf_path(chat_id: str) -> Path:
        file_name = CV_DIR / chat_id / "output"
        return str(file_name)
