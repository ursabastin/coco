from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import sqlite3
import json
import os

class TaskScheduler:
    def __init__(self, db_path="scheduler/tasks.db", task_executor=None):
        self.db_path = db_path
        self.task_executor = task_executor
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.scheduler = BackgroundScheduler()
        self.init_database()
        self.scheduler.start()
        print("[Scheduler] Background scheduler started")
    
    def init_database(self):
        """Initialize scheduler database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                schedule_type TEXT,
                schedule_config TEXT,
                task_config TEXT,
                enabled INTEGER,
                last_run TEXT,
                next_run TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def schedule_interval_task(self, name, minutes, task_config):
        """Schedule task to run every N minutes"""
        job = self.scheduler.add_job(
            self.execute_scheduled_task,
            IntervalTrigger(minutes=minutes),
            args=[task_config],
            id=name,
            replace_existing=True
        )
        
        # Save to database
        self.save_task_to_db(name, 'interval', {'minutes': minutes}, task_config)
        
        return f"Scheduled '{name}' to run every {minutes} minutes"
    
    def schedule_daily_task(self, name, hour, minute, task_config):
        """Schedule task to run daily at specific time"""
        job = self.scheduler.add_job(
            self.execute_scheduled_task,
            CronTrigger(hour=hour, minute=minute),
            args=[task_config],
            id=name,
            replace_existing=True
        )
        
        # Save to database
        self.save_task_to_db(name, 'daily', {'hour': hour, 'minute': minute}, task_config)
        
        return f"Scheduled '{name}' to run daily at {hour:02d}:{minute:02d}"
    
    def execute_scheduled_task(self, task_config):
        """Execute a scheduled task"""
        print(f"[Scheduler] Executing scheduled task: {task_config.get('name', 'Unnamed')}")
        
        if self.task_executor:
            steps = task_config.get('steps', [])
            if steps:
                self.task_executor.execute_multi_step_task(steps)
            else:
                # Single action
                self.task_executor.execute_step(task_config)
        
        # Update last run time
        self.update_last_run(task_config.get('name', 'unknown'))
    
    def save_task_to_db(self, name, schedule_type, schedule_config, task_config):
        """Save scheduled task to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO scheduled_tasks 
            (name, schedule_type, schedule_config, task_config, enabled, last_run, next_run)
            VALUES (?, ?, ?, ?, 1, NULL, NULL)
        """, (
            name,
            schedule_type,
            json.dumps(schedule_config),
            json.dumps(task_config),
        ))
        
        conn.commit()
        conn.close()
    
    def update_last_run(self, task_name):
        """Update last run timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE scheduled_tasks
            SET last_run = ?
            WHERE name = ?
        """, (datetime.now().isoformat(), task_name))
        
        conn.commit()
        conn.close()
    
    def list_scheduled_tasks(self):
        """List all scheduled tasks"""
        jobs = self.scheduler.get_jobs()
        
        tasks = []
        for job in jobs:
            tasks.append({
                'name': job.id,
                'next_run': str(job.next_run_time)
            })
        
        return tasks
    
    def remove_task(self, name):
        """Remove a scheduled task"""
        self.scheduler.remove_job(name)
        
        # Remove from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scheduled_tasks WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        
        return f"Removed scheduled task: {name}"
    
    def shutdown(self):
        """Shutdown scheduler"""
        self.scheduler.shutdown()
        print("[Scheduler] Scheduler shutdown")

# Test script
if __name__ == "__main__":
    import os
    os.makedirs('scheduler', exist_ok=True)
    
    scheduler = TaskScheduler()
    
    # Schedule a test task
    task_config = {
        'name': 'test_task',
        'intent': 'system.open_app',
        'parameters': {'app': 'notepad'}
    }
    
    print(scheduler.schedule_interval_task('test_task', 1, task_config))
    
    # List tasks
    print("\nScheduled tasks:")
    for task in scheduler.list_scheduled_tasks():
        print(f"  {task['name']}: Next run at {task['next_run']}")
    
    input("\nPress Enter to stop scheduler...")
    scheduler.shutdown()
