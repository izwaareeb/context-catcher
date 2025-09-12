import sqlite3

DB_NAME = "context.db"

def get_all_events():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, source, content, timestamp FROM events ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    events = get_all_events()
    for e in events:
        print(e)
