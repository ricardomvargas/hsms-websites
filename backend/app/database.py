import sqlite3

DB_PATH = "hsm.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kvk_number TEXT,
            website_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN website_url TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()
