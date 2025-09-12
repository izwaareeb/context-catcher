import sqlite3
import time

DB_FILE = "context.db"

def log_event(event: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (event) VALUES (?)",
        (event,)
    )
    conn.commit()
    conn.close()

def main():
    print("Listener started. Logging events every 5 seconds...")
    while True:
        log_event("Test Event")  # Replace later with real captured events
        time.sleep(5)

if __name__ == "__main__":
    main()