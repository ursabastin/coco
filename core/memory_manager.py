import sqlite3
import json
from datetime import datetime
import os

class MemoryManager:
    def __init__(self, db_path="data/memory/conversation.db"):
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.session_id = None
        self.init_database()
        self.start_session()
    
    def init_database(self):
        """Initialize database with required tables"""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        
        # Conversations table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                role TEXT,
                content TEXT,
                intent TEXT,
                action_result TEXT
            )
        """)
        
        # Sessions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                total_interactions INTEGER
            )
        """)
        
        self.connection.commit()
        print("[MemoryManager] Database initialized")
    
    def start_session(self):
        """Start a new conversation session"""
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.cursor.execute("""
            INSERT INTO sessions (session_id, start_time, total_interactions)
            VALUES (?, ?, 0)
        """, (self.session_id, datetime.now().isoformat()))
        
        self.connection.commit()
        print(f"[MemoryManager] Session started: {self.session_id}")
    
    def add_interaction(self, role, content, intent=None, action_result=None):
        """Add an interaction to memory"""
        self.cursor.execute("""
            INSERT INTO conversations (session_id, timestamp, role, content, intent, action_result)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.session_id,
            datetime.now().isoformat(),
            role,
            content,
            intent,
            action_result
        ))
        
        # Update session interaction count
        self.cursor.execute("""
            UPDATE sessions 
            SET total_interactions = total_interactions + 1
            WHERE session_id = ?
        """, (self.session_id,))
        
        self.connection.commit()
        print(f"[MemoryManager] Added {role} interaction")
    
    def get_recent_context(self, limit=5):
        """Get recent conversation for context"""
        self.cursor.execute("""
            SELECT role, content, intent, action_result
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (self.session_id, limit))
        
        rows = self.cursor.fetchall()
        
        # Format as conversation history (reverse to chronological order)
        context = []
        for row in reversed(rows):
            role, content, intent, action_result = row
            
            if role == "user":
                context.append(f"User: {content}")
            elif role == "assistant":
                if intent:
                    context.append(f"coco: [Executed: {intent}] {content}")
                else:
                    context.append(f"coco: {content}")
        
        return "\n".join(context)
    
    def get_last_mentioned_entity(self, entity_type):
        """Get last mentioned entity of a type (e.g., 'app', 'file', 'website')"""
        self.cursor.execute("""
            SELECT content, intent
            FROM conversations
            WHERE session_id = ?
            AND role = 'user'
            ORDER BY timestamp DESC
            LIMIT 10
        """, (self.session_id,))
        
        rows = self.cursor.fetchall()
        
        if entity_type == "app":
            apps = ["notepad", "calculator", "chrome", "edge", "paint"]
            for content, intent in rows:
                for app in apps:
                    if app in content.lower():
                        return app
        
        return None
    
    def end_session(self):
        """End the current session"""
        self.cursor.execute("""
            UPDATE sessions
            SET end_time = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), self.session_id))
        
        self.connection.commit()
        print(f"[MemoryManager] Session ended: {self.session_id}")
    
    def get_session_summary(self):
        """Get summary of current session"""
        self.cursor.execute("""
            SELECT total_interactions FROM sessions WHERE session_id = ?
        """, (self.session_id,))
        
        row = self.cursor.fetchone()
        count = row[0] if row else 0
        return f"Session {self.session_id}: {count} interactions"
    
    def close(self):
        """Close database connection"""
        self.end_session()
        if self.connection:
            self.connection.close()

# Test script
if __name__ == "__main__":
    memory = MemoryManager()
    
    # Simulate conversation
    memory.add_interaction("user", "Open notepad", intent="open_app")
    memory.add_interaction("assistant", "Opened notepad", action_result="Success")
    
    memory.add_interaction("user", "Type hello world", intent="type_text")
    memory.add_interaction("assistant", "Typed text", action_result="Success")
    
    memory.add_interaction("user", "Close it")
    
    # Get context
    print("\nRecent context:")
    print(memory.get_recent_context())
    
    # Find last mentioned app
    print(f"\nLast app mentioned: {memory.get_last_mentioned_entity('app')}")
    
    print(f"\n{memory.get_session_summary()}")
    
    memory.close()
    print("Memory manager working!")
