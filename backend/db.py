import sqlite3

DB_NAME = "context.db"

def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initialize tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    
    if __name__ == "__main__":
        init_db()
        print("Database initialized ✅")
