import sqlite3

def get_events():
    conn = sqlite3.connect("context.db")
    cur = conn.cursor()
    cur.execute("SELECT source, content, timestamp FROM events ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    events = get_events()
    for e in events:
        print(e)