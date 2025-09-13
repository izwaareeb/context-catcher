import sqlite3
import time
import json
import asyncio
from datetime import datetime
from backend.db import get_connection

class ContextListener:
    def __init__(self):
        self.conn = get_connection()
        self.running = False
        
    def log_event(self, source: str, content: str, metadata: dict = None):
        """Log an event to the database."""
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO events (source, content, metadata, timestamp)
            VALUES (?, ?, ?, ?)
        """, (source, content, metadata_json, datetime.now()))
        
        self.conn.commit()
        print(f"📝 Logged {source} event: {content[:50]}...")
    
    def simulate_slack_events(self):
        """Simulate Slack messages for demo purposes."""
        slack_events = [
            {
                "content": "Hey team, let's discuss the Q3 roadmap tomorrow at 2pm",
                "metadata": {"channel": "general", "user": "john_doe", "timestamp": datetime.now().isoformat()}
            },
            {
                "content": "The new feature is ready for testing. Can someone review the PR?",
                "metadata": {"channel": "dev-team", "user": "sarah_dev", "timestamp": datetime.now().isoformat()}
            },
            {
                "content": "Meeting moved to 3pm due to client call",
                "metadata": {"channel": "general", "user": "mike_manager", "timestamp": datetime.now().isoformat()}
            }
        ]
        
        for event in slack_events:
            self.log_event("Slack", event["content"], event["metadata"])
    
    def simulate_gmail_events(self):
        """Simulate Gmail messages for demo purposes."""
        gmail_events = [
            {
                "content": "Subject: Project Update - Q3 Milestones\nHi team, here's the latest update on our Q3 goals. We're on track for the major deliverables.",
                "metadata": {"sender": "client@company.com", "subject": "Project Update - Q3 Milestones", "timestamp": datetime.now().isoformat()}
            },
            {
                "content": "Subject: Invoice #12345\nPlease find attached the invoice for this month's services. Due date: 30 days.",
                "metadata": {"sender": "billing@vendor.com", "subject": "Invoice #12345", "timestamp": datetime.now().isoformat()}
            },
            {
                "content": "Subject: Meeting Request - Product Demo\nHi, I'd like to schedule a product demo for next week. Are you available Tuesday or Wednesday?",
                "metadata": {"sender": "prospect@newclient.com", "subject": "Meeting Request - Product Demo", "timestamp": datetime.now().isoformat()}
            }
        ]
        
        for event in gmail_events:
            self.log_event("Gmail", event["content"], event["metadata"])
    
    def simulate_notion_events(self):
        """Simulate Notion page updates for demo purposes."""
        notion_events = [
            {
                "content": "Updated Q3 Goals page: Added new milestone for user authentication feature",
                "metadata": {"page": "Q3 Goals", "action": "updated", "timestamp": datetime.now().isoformat()}
            },
            {
                "content": "Created new task: Review competitor analysis by Friday",
                "metadata": {"page": "Tasks", "action": "created", "timestamp": datetime.now().isoformat()}
            },
            {
                "content": "Updated meeting notes: Added action items from today's standup",
                "metadata": {"page": "Meeting Notes", "action": "updated", "timestamp": datetime.now().isoformat()}
            }
        ]
        
        for event in notion_events:
            self.log_event("Notion", event["content"], event["metadata"])
    
    def simulate_zoom_events(self):
        """Simulate Zoom meeting events for demo purposes."""
        zoom_events = [
            {
                "content": "Meeting: Daily Standup - Duration: 30 minutes - Participants: 5",
                "metadata": {"meeting": "Daily Standup", "duration": 30, "participants": 5, "timestamp": datetime.now().isoformat()}
            },
            {
                "content": "Meeting: Client Demo - Duration: 60 minutes - Participants: 8",
                "metadata": {"meeting": "Client Demo", "duration": 60, "participants": 8, "timestamp": datetime.now().isoformat()}
            }
        ]
        
        for event in zoom_events:
            self.log_event("Zoom", event["content"], event["metadata"])
    
    def simulate_yesterday_events(self):
        """Simulate events from yesterday for the recap feature."""
        yesterday_events = [
            {
                "source": "Slack",
                "content": "Completed the user authentication feature implementation",
                "metadata": {"channel": "dev-team", "user": "sarah_dev", "timestamp": "2024-01-14T10:30:00"}
            },
            {
                "source": "Gmail",
                "content": "Subject: Client Feedback - Great work on the demo!\nThe client was very impressed with our presentation.",
                "metadata": {"sender": "client@company.com", "subject": "Client Feedback", "timestamp": "2024-01-14T15:45:00"}
            },
            {
                "source": "Notion",
                "content": "Updated project timeline: Moved launch date to next week",
                "metadata": {"page": "Project Timeline", "action": "updated", "timestamp": "2024-01-14T16:20:00"}
            },
            {
                "source": "Zoom",
                "content": "Meeting: Client Demo - Duration: 45 minutes - Status: Successful",
                "metadata": {"meeting": "Client Demo", "duration": 45, "status": "successful", "timestamp": "2024-01-14T14:00:00"}
            }
        ]
        
        for event in yesterday_events:
            self.log_event(event["source"], event["content"], event["metadata"])
    
    def simulate_today_tasks(self):
        """Simulate today's tasks for the planning feature."""
        today_tasks = [
            {
                "source": "Notion",
                "content": "Review and approve the new feature PR",
                "metadata": {"page": "Tasks", "priority": "high", "due": "today", "timestamp": datetime.now().isoformat()}
            },
            {
                "source": "Calendar",
                "content": "Team standup meeting at 10:00 AM",
                "metadata": {"type": "meeting", "time": "10:00", "timestamp": datetime.now().isoformat()}
            },
            {
                "source": "Slack",
                "content": "Follow up with client about contract renewal",
                "metadata": {"channel": "sales", "priority": "medium", "timestamp": datetime.now().isoformat()}
            },
            {
                "source": "Gmail",
                "content": "Respond to vendor pricing inquiry",
                "metadata": {"sender": "vendor@supplier.com", "priority": "medium", "timestamp": datetime.now().isoformat()}
            }
        ]
        
        for task in today_tasks:
            self.log_event(task["source"], task["content"], task["metadata"])
    
    async def start_listening(self):
        """Start the context listening service."""
        print("🎧 Context Listener started...")
        self.running = True
        
        # Simulate some initial data for demo
        print("📊 Loading demo data...")
        self.simulate_yesterday_events()
        self.simulate_today_tasks()
        
        # Simulate ongoing events
        while self.running:
            try:
                # Simulate new events every 30 seconds
                await asyncio.sleep(30)
                
                # Randomly add new events
                import random
                event_sources = [
                    self.simulate_slack_events,
                    self.simulate_gmail_events,
                    self.simulate_notion_events,
                    self.simulate_zoom_events
                ]
                
                # Pick a random source and add one event
                source_func = random.choice(event_sources)
                source_func()
                
            except KeyboardInterrupt:
                print("🛑 Stopping listener...")
                self.running = False
                break
    
    def stop_listening(self):
        """Stop the context listening service."""
        self.running = False
        self.conn.close()

# Legacy function for backward compatibility
def log_event(event: str):
    listener = ContextListener()
    listener.log_event("Test", event)
    listener.conn.close()

def main():
    listener = ContextListener()
    try:
        asyncio.run(listener.start_listening())
    except KeyboardInterrupt:
        listener.stop_listening()

if __name__ == "__main__":
    main()