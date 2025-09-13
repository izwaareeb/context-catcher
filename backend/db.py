import sqlite3
import json
from datetime import datetime

DB_NAME = "context.db"

def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initialize tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Events table (enhanced from your original)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        content TEXT NOT NULL,
        metadata TEXT,  -- JSON for additional data
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT FALSE
    )
    """)
    
    # Embeddings table for GPT-5 embeddings
    cur.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        embedding TEXT,  -- JSON array of embedding values
        model TEXT DEFAULT 'gpt-5',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    """)
    
    # Threads table for organizing related events
    cur.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'  -- active, archived, completed
    )
    """)
    
    # Thread events junction table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS thread_events (
        thread_id INTEGER,
        event_id INTEGER,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (thread_id, event_id),
        FOREIGN KEY (thread_id) REFERENCES threads (id),
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    """)
    
    # Voice briefings table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS voice_briefings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        briefing_type TEXT NOT NULL,  -- daily, weekly, custom
        content TEXT NOT NULL,
        audio_file_path TEXT,
        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        played BOOLEAN DEFAULT FALSE
    )
    """)
    
    # User commands table for voice commands
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command_text TEXT NOT NULL,
        parsed_intent TEXT,  -- JSON of parsed command
        executed BOOLEAN DEFAULT FALSE,
        result TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized with enhanced schema ✅")

if __name__ == "__main__":
    init_db()
