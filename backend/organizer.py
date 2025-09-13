import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from backend.db import get_connection

# Note: You'll need to install openai and numpy
# pip install openai numpy

class ContextOrganizer:
    def __init__(self):
        self.conn = get_connection()
        # You'll set your OpenAI API key in config/settings.py
        # self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def fetch_unprocessed_events(self, limit: int = 50):
        """Fetch unprocessed events from the database."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, source, content, metadata, timestamp 
            FROM events 
            WHERE processed = FALSE 
            ORDER BY timestamp ASC 
            LIMIT ?
        """, (limit,))
        return cur.fetchall()
    
    def create_embedding(self, text: str):
        """Create GPT-5 embedding for text content."""
        # Placeholder for OpenAI embedding call
        # In real implementation, you'd call:
        # response = self.openai_client.embeddings.create(
        #     model="text-embedding-3-large",
        #     input=text
        # )
        # return response.data[0].embedding
        
        # For now, return a mock embedding (you'll replace this)
        return [0.1] * 1536  # Mock embedding vector
    
    def store_embedding(self, event_id: int, embedding: list):
        """Store embedding in the database."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO embeddings (event_id, embedding, model)
            VALUES (?, ?, ?)
        """, (event_id, json.dumps(embedding), 'gpt-5'))
        self.conn.commit()
    
    def find_similar_events(self, event_id: int, threshold: float = 0.8):
        """Find events similar to the given event using embeddings."""
        cur = self.conn.cursor()
        
        # Get the embedding for the current event
        cur.execute("SELECT embedding FROM embeddings WHERE event_id = ?", (event_id,))
        current_embedding = cur.fetchone()
        
        if not current_embedding:
            return []
        
        current_vec = np.array(json.loads(current_embedding[0]))
        
        # Get all other embeddings
        cur.execute("SELECT event_id, embedding FROM embeddings WHERE event_id != ?", (event_id,))
        all_embeddings = cur.fetchall()
        
        similar_events = []
        for other_event_id, other_embedding in all_embeddings:
            other_vec = np.array(json.loads(other_embedding))
            
            # Calculate cosine similarity
            similarity = np.dot(current_vec, other_vec) / (np.linalg.norm(current_vec) * np.linalg.norm(other_vec))
            
            if similarity > threshold:
                similar_events.append((other_event_id, similarity))
        
        return sorted(similar_events, key=lambda x: x[1], reverse=True)
    
    def create_thread(self, title: str, description: str = ""):
        """Create a new thread for organizing related events."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO threads (title, description)
            VALUES (?, ?)
        """, (title, description))
        self.conn.commit()
        return cur.lastrowid
    
    def add_event_to_thread(self, thread_id: int, event_id: int):
        """Add an event to a thread."""
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO thread_events (thread_id, event_id)
                VALUES (?, ?)
            """, (thread_id, event_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Event already in thread
            return False
    
    def organize_events_into_threads(self):
        """Main function to organize events into intelligent threads."""
        print("🧠 Starting intelligent event organization...")
        
        # Get unprocessed events
        events = self.fetch_unprocessed_events()
        print(f"📥 Found {len(events)} unprocessed events")
        
        for event in events:
            event_id, source, content, metadata, timestamp = event
            
            # Create embedding for this event
            embedding = self.create_embedding(content)
            self.store_embedding(event_id, embedding)
            
            # Find similar events
            similar_events = self.find_similar_events(event_id)
            
            if similar_events:
                # Check if any similar events are already in threads
                cur = self.conn.cursor()
                cur.execute("""
                    SELECT DISTINCT thread_id FROM thread_events 
                    WHERE event_id IN ({})
                """.format(','.join('?' * len(similar_events))), 
                [event[0] for event in similar_events])
                
                existing_threads = [row[0] for row in cur.fetchall()]
                
                if existing_threads:
                    # Add to existing thread
                    thread_id = existing_threads[0]
                    self.add_event_to_thread(thread_id, event_id)
                    print(f"📎 Added event {event_id} to existing thread {thread_id}")
                else:
                    # Create new thread
                    thread_title = f"Thread: {source} - {content[:50]}..."
                    thread_id = self.create_thread(thread_title, f"Auto-generated thread for {source} events")
                    
                    # Add current event and similar events to thread
                    self.add_event_to_thread(thread_id, event_id)
                    for similar_event_id, _ in similar_events[:3]:  # Limit to top 3 similar
                        self.add_event_to_thread(thread_id, similar_event_id)
                    
                    print(f"🆕 Created new thread {thread_id}: {thread_title}")
            else:
                # Create individual thread for unique event
                thread_title = f"Individual: {source} - {content[:50]}..."
                thread_id = self.create_thread(thread_title, f"Individual event from {source}")
                self.add_event_to_thread(thread_id, event_id)
                print(f"🔹 Created individual thread {thread_id} for event {event_id}")
            
            # Mark event as processed
            cur = self.conn.cursor()
            cur.execute("UPDATE events SET processed = TRUE WHERE id = ?", (event_id,))
            self.conn.commit()
        
        print("✅ Event organization complete!")
    
    def get_thread_summary(self, thread_id: int):
        """Get a summary of events in a thread."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT e.source, e.content, e.timestamp
            FROM events e
            JOIN thread_events te ON e.id = te.event_id
            WHERE te.thread_id = ?
            ORDER BY e.timestamp
        """, (thread_id,))
        
        events = cur.fetchall()
        return {
            'thread_id': thread_id,
            'event_count': len(events),
            'sources': list(set([event[0] for event in events])),
            'events': events
        }
    
    def get_all_threads(self):
        """Get all threads with their summaries."""
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, description, created_at FROM threads ORDER BY updated_at DESC")
        threads = cur.fetchall()
        
        thread_summaries = []
        for thread in threads:
            thread_id, title, description, created_at = thread
            summary = self.get_thread_summary(thread_id)
            thread_summaries.append({
                'id': thread_id,
                'title': title,
                'description': description,
                'created_at': created_at,
                'summary': summary
            })
        
        return thread_summaries

# Legacy functions for backward compatibility
def fetch_events(limit: int = 10):
    """Fetch the most recent events from the DB."""
    organizer = ContextOrganizer()
    cur = organizer.conn.cursor()
    cur.execute("SELECT id, source, content, timestamp FROM events ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    organizer.conn.close()
    return rows

def group_by_source(events):
    """Naive grouping: cluster events by source (Slack, Gmail, etc.)."""
    grouped = {}
    for e in events:
        source = e[1]  # second column = source
        grouped.setdefault(source, []).append(e)
    return grouped

if __name__ == "__main__":
    organizer = ContextOrganizer()
    
    # Run the intelligent organization
    organizer.organize_events_into_threads()
    
    # Show results
    threads = organizer.get_all_threads()
    print(f"\n📊 Found {len(threads)} threads:")
    for thread in threads:
        print(f"🔹 Thread {thread['id']}: {thread['title']}")
        print(f"   Events: {thread['summary']['event_count']}, Sources: {', '.join(thread['summary']['sources'])}")
