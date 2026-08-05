import sqlite3
import logging
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../../data/trendly.db")


class DatabaseManager:
    @classmethod
    def init_db(cls):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                summary TEXT,
                status TEXT DEFAULT 'open',
                resolution TEXT
            )
        """)
        conn.commit()
        conn.close()
        logging.info("SQLite Database initialized.")

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(DB_PATH)


db_manager = DatabaseManager()
