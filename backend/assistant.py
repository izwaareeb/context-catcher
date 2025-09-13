import json
import asyncio
import webbrowser
import subprocess
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_connection
from backend.organizer import ContextOrganizer

class ContextAssistant:
    def __init__(self):
        self.conn = get_connection()
        self.organizer = ContextOrganizer()
        # You'll add ElevenLabs and OpenAI clients here when you have API keys
        # self.elevenlabs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        # self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def get_yesterday_events(self):
        """Get events from yesterday for the recap."""
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        cur = self.conn.cursor()
        cur.execute("""
            SELECT source, content, metadata, timestamp
            FROM events
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, (yesterday_start, yesterday_end))
        
        return cur.fetchall()
    
    def get_today_tasks(self):
        """Get today's tasks and meetings."""
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        cur = self.conn.cursor()
        cur.execute("""
            SELECT source, content, metadata, timestamp
            FROM events
            WHERE timestamp BETWEEN ? AND ?
            AND (source = 'Calendar' OR source = 'Notion' OR 
                 (source = 'Slack' AND content LIKE '%task%') OR
                 (source = 'Gmail' AND content LIKE '%urgent%'))
            ORDER BY timestamp ASC
        """, (today_start, today_end))
        
        return cur.fetchall()
    
    def generate_yesterday_recap(self):
        """Generate a voice recap of yesterday's activities."""
        events = self.get_yesterday_events()
        
        if not events:
            return "Yesterday was a quiet day with no recorded activities."
        
        # Group events by source
        sources = {}
        for event in events:
            source, content, metadata, timestamp = event
            if source not in sources:
                sources[source] = []
            sources[source].append((content, timestamp))
        
        # Generate recap text
        recap_parts = ["Here's your recap from yesterday:"]
        
        for source, source_events in sources.items():
            recap_parts.append(f"In {source}, you had {len(source_events)} activities:")
            for content, timestamp in source_events[:3]:  # Limit to top 3 per source
                time_str = timestamp.strftime("%I:%M %p")
                recap_parts.append(f"At {time_str}: {content[:100]}...")
        
        recap_text = " ".join(recap_parts)
        
        # Store the briefing
        self.store_voice_briefing("daily", recap_text, "yesterday_recap")
        
        return recap_text
    
    def generate_today_plan(self):
        """Generate a voice briefing of today's plan."""
        tasks = self.get_today_tasks()
        
        if not tasks:
            return "You have a light day ahead with no specific tasks scheduled."
        
        # Categorize tasks
        meetings = []
        high_priority = []
        medium_priority = []
        
        for task in tasks:
            source, content, metadata, timestamp = task
            metadata_dict = json.loads(metadata) if metadata else {}
            
            if source == "Calendar" or "meeting" in content.lower():
                meetings.append((content, timestamp))
            elif metadata_dict.get("priority") == "high":
                high_priority.append((content, timestamp))
            else:
                medium_priority.append((content, timestamp))
        
        # Generate plan text
        plan_parts = ["Here's your plan for today:"]
        
        if meetings:
            plan_parts.append(f"You have {len(meetings)} meetings scheduled:")
            for content, timestamp in meetings:
                time_str = timestamp.strftime("%I:%M %p")
                plan_parts.append(f"At {time_str}: {content}")
        
        if high_priority:
            plan_parts.append(f"You have {len(high_priority)} high-priority tasks:")
            for content, timestamp in high_priority:
                plan_parts.append(f"• {content}")
        
        if medium_priority:
            plan_parts.append(f"And {len(medium_priority)} medium-priority items to review.")
        
        plan_text = " ".join(plan_parts)
        
        # Store the briefing
        self.store_voice_briefing("daily", plan_text, "today_plan")
        
        return plan_text
    
    def store_voice_briefing(self, briefing_type: str, content: str, audio_file_path: str = None):
        """Store a voice briefing in the database."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO voice_briefings (briefing_type, content, audio_file_path)
            VALUES (?, ?, ?)
        """, (briefing_type, content, audio_file_path))
        self.conn.commit()
    
    def parse_command(self, command_text: str):
        """Parse a voice command using GPT-5 reasoning."""
        # Placeholder for GPT-5 command parsing
        # In real implementation, you'd call:
        # response = self.openai_client.chat.completions.create(
        #     model="gpt-5",
        #     messages=[{"role": "user", "content": f"Parse this command: {command_text}"}]
        # )
        
        # For demo, we'll do simple keyword matching
        command_lower = command_text.lower()
        
        if "gmail" in command_lower or "email" in command_lower:
            return {
                "action": "open_app",
                "app": "gmail",
                "url": "https://gmail.com",
                "description": "Opening Gmail"
            }
        elif "youtube" in command_lower and "search" in command_lower:
            # Extract search term
            search_term = command_lower.replace("search youtube for", "").replace("youtube", "").strip()
            return {
                "action": "search_youtube",
                "query": search_term,
                "url": f"https://youtube.com/results?search_query={search_term.replace(' ', '+')}",
                "description": f"Searching YouTube for {search_term}"
            }
        elif "google" in command_lower and "search" in command_lower:
            # Extract search term
            search_term = command_lower.replace("google", "").replace("search", "").strip()
            return {
                "action": "search_google",
                "query": search_term,
                "url": f"https://google.com/search?q={search_term.replace(' ', '+')}",
                "description": f"Searching Google for {search_term}"
            }
        elif "notion" in command_lower:
            return {
                "action": "open_app",
                "app": "notion",
                "url": "https://notion.so",
                "description": "Opening Notion"
            }
        elif "slack" in command_lower:
            return {
                "action": "open_app",
                "app": "slack",
                "url": "https://slack.com",
                "description": "Opening Slack"
            }
        else:
            return {
                "action": "unknown",
                "description": f"Command not recognized: {command_text}"
            }
    
    def execute_command(self, parsed_command: dict):
        """Execute a parsed command."""
        action = parsed_command.get("action")
        
        if action == "open_app" or action == "search_youtube" or action == "search_google":
            url = parsed_command.get("url")
            if url:
                webbrowser.open(url)
                return f"✅ {parsed_command.get('description', 'Command executed')}"
        
        elif action == "unknown":
            return f"❌ {parsed_command.get('description', 'Command not recognized')}"
        
        return f"✅ {parsed_command.get('description', 'Command executed')}"
    
    def process_voice_command(self, command_text: str):
        """Process a voice command from the user."""
        # Store the command
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO user_commands (command_text, timestamp)
            VALUES (?, ?)
        """, (command_text, datetime.now()))
        command_id = cur.lastrowid
        
        # Parse the command
        parsed_command = self.parse_command(command_text)
        
        # Update the command with parsed intent
        cur.execute("""
            UPDATE user_commands 
            SET parsed_intent = ?
            WHERE id = ?
        """, (json.dumps(parsed_command), command_id))
        
        # Execute the command
        result = self.execute_command(parsed_command)
        
        # Update the command with result
        cur.execute("""
            UPDATE user_commands 
            SET executed = TRUE, result = ?
            WHERE id = ?
        """, (result, command_id))
        
        self.conn.commit()
        
        return {
            "command_id": command_id,
            "parsed_command": parsed_command,
            "result": result
        }
    
    def generate_voice_audio(self, text: str, filename: str):
        """Generate voice audio using ElevenLabs."""
        # Placeholder for ElevenLabs TTS
        # In real implementation, you'd call:
        # audio = self.elevenlabs_client.generate(
        #     text=text,
        #     voice="Rachel",  # or your preferred voice
        #     model="eleven_multilingual_v2"
        # )
        # with open(f"audio/{filename}.mp3", "wb") as f:
        #     f.write(audio)
        
        print(f"🔊 [Voice Audio Generated]: {text[:100]}...")
        return f"audio/{filename}.mp3"
    
    def play_voice_briefing(self, briefing_type: str):
        """Play a voice briefing."""
        if briefing_type == "yesterday":
            text = self.generate_yesterday_recap()
            filename = "yesterday_recap"
        elif briefing_type == "today":
            text = self.generate_today_plan()
            filename = "today_plan"
        else:
            return "Invalid briefing type"
        
        # Generate and play audio
        audio_file = self.generate_voice_audio(text, filename)
        
        # In a real implementation, you'd play the audio file
        print(f"🎵 Playing: {text}")
        
        return {
            "text": text,
            "audio_file": audio_file,
            "type": briefing_type
        }
    
    def get_system_status(self):
        """Get the current status of the Context Catcher system."""
        cur = self.conn.cursor()
        
        # Get event counts
        cur.execute("SELECT COUNT(*) FROM events")
        total_events = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM events WHERE processed = FALSE")
        unprocessed_events = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM threads")
        total_threads = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM voice_briefings")
        total_briefings = cur.fetchone()[0]
        
        return {
            "total_events": total_events,
            "unprocessed_events": unprocessed_events,
            "total_threads": total_threads,
            "total_briefings": total_briefings,
            "status": "running" if unprocessed_events < 10 else "needs_attention"
        }

# Main functions for the API
def get_yesterday_recap():
    """Get yesterday's recap briefing."""
    assistant = ContextAssistant()
    return assistant.play_voice_briefing("yesterday")

def get_today_plan():
    """Get today's plan briefing."""
    assistant = ContextAssistant()
    return assistant.play_voice_briefing("today")

def process_command(command_text: str):
    """Process a voice command."""
    assistant = ContextAssistant()
    return assistant.process_voice_command(command_text)

def get_system_status():
    """Get system status."""
    assistant = ContextAssistant()
    return assistant.get_system_status()

if __name__ == "__main__":
    assistant = ContextAssistant()
    
    print("🤖 Context Catcher Assistant")
    print("=" * 40)
    
    # Test yesterday recap
    print("\n📅 Yesterday's Recap:")
    yesterday_recap = assistant.play_voice_briefing("yesterday")
    print(yesterday_recap["text"])
    
    # Test today's plan
    print("\n📋 Today's Plan:")
    today_plan = assistant.play_voice_briefing("today")
    print(today_plan["text"])
    
    # Test command processing
    print("\n🎤 Testing Commands:")
    test_commands = [
        "Open Gmail",
        "Search YouTube for lo-fi music",
        "Google vendor pricing",
        "Open Notion Q3 doc"
    ]
    
    for cmd in test_commands:
        result = assistant.process_voice_command(cmd)
        print(f"Command: {cmd}")
        print(f"Result: {result['result']}")
        print()
    
    # Show system status
    print("📊 System Status:")
    status = assistant.get_system_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
