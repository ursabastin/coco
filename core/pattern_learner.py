import sqlite3
from datetime import datetime, timedelta
from collections import Counter
import os

class PatternLearner:
    def __init__(self, db_path="data/memory/patterns.db", conversation_db="data/memory/conversation.db"):
        self.db_path = db_path
        self.conversation_db = conversation_db
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.init_database()
        print("[PatternLearner] Initialized")
    
    def init_database(self):
        """Initialize patterns database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                intent TEXT,
                frequency INTEGER,
                last_used TEXT,
                time_of_day TEXT,
                day_of_week TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_command(self, command, intent):
        """Log a command for pattern analysis"""
        now = datetime.now()
        time_of_day = self.get_time_period(now.hour)
        day_of_week = now.strftime('%A')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if command already exists
        cursor.execute("""
            SELECT id, frequency FROM command_patterns 
            WHERE command = ? AND intent = ?
        """, (command, intent))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing
            pattern_id, frequency = result
            cursor.execute("""
                UPDATE command_patterns
                SET frequency = ?, last_used = ?, time_of_day = ?, day_of_week = ?
                WHERE id = ?
            """, (frequency + 1, now.isoformat(), time_of_day, day_of_week, pattern_id))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO command_patterns (command, intent, frequency, last_used, time_of_day, day_of_week)
                VALUES (?, ?, 1, ?, ?, ?)
            """, (command, intent, now.isoformat(), time_of_day, day_of_week))
        
        conn.commit()
        conn.close()
    
    def get_time_period(self, hour):
        """Get time period from hour"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def get_frequent_commands(self, limit=10):
        """Get most frequently used commands"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT command, intent, frequency
            FROM command_patterns
            ORDER BY frequency DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [(cmd, intent, freq) for cmd, intent, freq in results]
    
    def suggest_command_for_time(self):
        """Suggest command based on current time"""
        now = datetime.now()
        time_of_day = self.get_time_period(now.hour)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT command, intent, frequency
            FROM command_patterns
            WHERE time_of_day = ?
            ORDER BY frequency DESC
            LIMIT 3
        """, (time_of_day,))
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            return [(cmd, intent) for cmd, intent, _ in results]
        return []
    
    def get_usage_statistics(self):
        """Get overall usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM command_patterns")
        unique_commands = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(frequency) FROM command_patterns")
        total_uses = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'unique_commands': unique_commands,
            'total_uses': total_uses,
            'average_uses': total_uses / unique_commands if unique_commands > 0 else 0
        }

# Test script
if __name__ == "__main__":
    learner = PatternLearner()
    
    # Simulate usage
    learner.log_command("Open notepad", "system.open_app")
    learner.log_command("Open notepad", "system.open_app")
    learner.log_command("Search google", "browser.search_google")
    
    print("\nFrequent commands:")
    for cmd, intent, freq in learner.get_frequent_commands():
        print(f"  {cmd} ({intent}): {freq} times")
    
    print("\nSuggestions for current time:")
    for cmd, intent in learner.suggest_command_for_time():
        print(f"  {cmd}")
    
    stats = learner.get_usage_statistics()
    print(f"\nStats: {stats['unique_commands']} unique commands, {stats['total_uses']} total uses")
