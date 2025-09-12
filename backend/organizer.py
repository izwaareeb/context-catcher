import sqlite3
from backend.db import get_connection

def fetch_events(limit: int = 10):
    """Fetch the most recent events from the DB."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, source, content, timestamp FROM events ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def group_by_source(events):
    """Naive grouping: cluster events by source (Slack, Gmail, etc.)."""
    grouped = {}
    for e in events:
        source = e[1]  # second column = source
        grouped.setdefault(source, []).append(e)
    return grouped

if __name__ == "__main__":
    events = fetch_events()
    grouped = group_by_source(events)
    for src, items in grouped.items():
        print(f"🔹 Source: {src}")
        for i in items:
            print(f"   - {i[2]} ({i[3]})")
