import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_connection
from backend.listener import ContextListener

def create_demo_data():
    """Create demo data for the Context Catcher."""
    print("🎭 Creating demo data...")
    
    listener = ContextListener()
    
    # Clear existing data
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events")
    cur.execute("DELETE FROM embeddings")
    cur.execute("DELETE FROM threads")
    cur.execute("DELETE FROM thread_events")
    cur.execute("DELETE FROM voice_briefings")
    cur.execute("DELETE FROM user_commands")
    conn.commit()
    
    # Add yesterday's events
    print("📅 Adding yesterday's events...")
    listener.simulate_yesterday_events()
    
    # Add today's tasks
    print("📋 Adding today's tasks...")
    listener.simulate_today_tasks()
    
    # Add some current events
    print("📝 Adding current events...")
    listener.simulate_slack_events()
    listener.simulate_gmail_events()
    listener.simulate_notion_events()
    listener.simulate_zoom_events()
    
    conn.close()
    print("✅ Demo data created successfully!")
    
    # Show summary
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events")
    event_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM events WHERE source = 'Gmail'")
    gmail_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM events WHERE source = 'Slack'")
    slack_count = cur.fetchone()[0]
    conn.close()
    
    print(f"📊 Created {event_count} total events:")
    print(f"   �� Gmail: {gmail_count}")
    print(f"   💬 Slack: {slack_count}")
    print(f"   📝 Notion: {event_count - gmail_count - slack_count}")

if __name__ == "__main__":
    create_demo_data()