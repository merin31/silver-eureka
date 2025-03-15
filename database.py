import sqlite3
import contextlib
import hashlib

class DatabaseManager:
    DB_FILE = "db.sqlite"

    def __init__(self):
        self.conn = sqlite3.connect(
            self.DB_FILE,
            timeout=10,
            check_same_thread=False
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=()):
        with contextlib.closing(self.conn) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(query, params)
                    # self.conn.commit()
        # self.cursor.execute(query, params)
        # self.conn.commit()

    def fetch_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
