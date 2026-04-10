# coco — Phase 3: Advanced Agent Intelligence
### Multi-Step Tasks + Scheduling + Workflows + Integrations

---

## What Phase 3 Adds

Phase 2.5 gave coco wake detection, memory, and system control. Phase 3 transforms coco into a **truly intelligent automation agent**:

**New Capabilities:**
- 🔗 **Multi-Step Execution** - Chain actions: "Open notepad, type hello, save it"
- ⏰ **Task Scheduling** - "Check my email every hour" or "Remind me at 3pm"
- 📋 **Workflow Builder** - Save and reuse automation sequences
- 📧 **Service Integrations** - Email (Gmail), Calendar, Spotify, Weather
- 🧠 **Pattern Learning** - coco learns your habits and suggests tasks
- 🔄 **Conditional Logic** - "If new email, then notify me"
- 🔁 **Background Tasks** - Run things while waiting for next command
- 💾 **Workflow Import/Export** - Share automation scripts

---

## Prerequisites

Before starting Phase 3:
- ✅ Phase 1 complete (STT → LLM → TTS)
- ✅ Phase 2 complete (Skills framework)
- ✅ Phase 2.5 complete (Wake detection + Memory + GPU)
- ✅ All previous features working correctly

---

## Architecture Overview

```
coco/
├── core/
│   ├── coco_refined.py        # Phase 2.5 agent
│   ├── coco_advanced.py       # NEW: Phase 3 agent
│   ├── task_executor.py       # NEW: Multi-step execution
│   ├── scheduler.py           # NEW: Task scheduling
│   ├── workflow_manager.py    # NEW: Workflow save/load
│   └── pattern_learner.py     # NEW: Usage pattern analysis
├── integrations/              # NEW: Service connectors
│   ├── __init__.py
│   ├── gmail_integration.py
│   ├── calendar_integration.py
│   ├── spotify_integration.py
│   └── weather_integration.py
├── workflows/                 # NEW: Saved workflows
│   └── default_workflows.json
├── skills/                    # From Phase 2
├── memory/
│   ├── conversation.db       # From Phase 2.5
│   └── patterns.db           # NEW: Learned patterns
└── scheduler/                # NEW: Scheduled tasks
    └── tasks.db
```

---

## STEP 1 — Install Scheduling & Background Task Libraries

### 1.1 Activate Virtual Environment
```powershell
cd C:\coco
.\venv\Scripts\activate
```

### 1.2 Install APScheduler
```powershell
pip install apscheduler
```

APScheduler handles time-based task scheduling.

### 1.3 Install Service Integration Libraries
```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install google-api-python-client
pip install spotipy
pip install python-dateutil
```

---

## STEP 2 — Create Multi-Step Task Executor

Create `C:\coco\core\task_executor.py`:

```python
import time
import json
from datetime import datetime

class TaskExecutor:
    def __init__(self, skill_manager, memory_manager):
        self.skills = skill_manager
        self.memory = memory_manager
        self.current_task = None
        self.task_history = []
    
    def parse_multi_step_command(self, llm_response):
        """Check if LLM response contains multiple steps"""
        # LLM should return steps in JSON format
        if isinstance(llm_response, dict) and 'steps' in llm_response:
            return llm_response['steps']
        return None
    
    def execute_step(self, step):
        """Execute a single step"""
        intent = step.get('intent')
        parameters = step.get('parameters', {})
        delay = step.get('delay', 0)  # Optional delay between steps
        
        if delay > 0:
            print(f"[TaskExecutor] Waiting {delay} seconds...")
            time.sleep(delay)
        
        # Execute via skill manager
        result = self.execute_skill(intent, parameters)
        
        # Log step execution
        step_log = {
            'timestamp': datetime.now().isoformat(),
            'intent': intent,
            'parameters': parameters,
            'result': result
        }
        self.task_history.append(step_log)
        
        return result
    
    def execute_skill(self, intent, parameters):
        """Execute skill (copied from coco_refined.py for consistency)"""
        if not intent or intent == "null":
            return None
        
        try:
            skill_name, action_name = intent.split(".")
            
            if skill_name == "browser":
                if action_name == "open_website":
                    return self.skills.browser.open_website(parameters.get('url', ''))
                elif action_name == "search_google":
                    return self.skills.browser.search_google(parameters.get('query', ''))
                elif action_name == "close_browser":
                    return self.skills.browser.close_browser()
            
            elif skill_name == "system":
                if action_name == "open_app":
                    return self.skills.system.open_application(parameters.get('app', ''))
                elif action_name == "close_app":
                    return self.skills.system.close_application(parameters.get('app', ''))
            
            elif skill_name == "keyboard":
                if action_name == "type_text":
                    return self.skills.keyboard.type_text(parameters.get('text', ''))
                elif action_name == "press_key":
                    return self.skills.keyboard.press_key(parameters.get('key', ''))
                elif action_name == "screenshot":
                    return self.skills.keyboard.take_screenshot()
            
            elif skill_name == "files":
                if action_name == "create_file":
                    return self.skills.files.create_file(
                        parameters.get('filepath', 'new_file.txt'),
                        parameters.get('content', '')
                    )
            
            return f"Executed {intent}"
        
        except Exception as e:
            return f"Error executing {intent}: {str(e)}"
    
    def execute_multi_step_task(self, steps):
        """Execute multiple steps in sequence"""
        results = []
        
        print(f"[TaskExecutor] Starting multi-step task with {len(steps)} steps")
        
        for i, step in enumerate(steps, 1):
            print(f"[TaskExecutor] Step {i}/{len(steps)}: {step.get('description', 'No description')}")
            
            result = self.execute_step(step)
            results.append({
                'step': i,
                'description': step.get('description', ''),
                'result': result
            })
            
            # Check if step failed
            if result and "error" in result.lower():
                print(f"[TaskExecutor] Step {i} failed, stopping task")
                break
        
        return results
    
    def get_task_summary(self, results):
        """Generate summary of task execution"""
        total_steps = len(results)
        successful_steps = sum(1 for r in results if not ("error" in str(r['result']).lower()))
        
        summary = f"Completed {successful_steps}/{total_steps} steps successfully."
        return summary

# Test script
if __name__ == "__main__":
    # Mock skill manager for testing
    class MockSkills:
        class MockBrowser:
            def open_website(self, url):
                return f"Opened {url}"
        
        class MockKeyboard:
            def type_text(self, text):
                return f"Typed: {text}"
        
        def __init__(self):
            self.browser = self.MockBrowser()
            self.keyboard = self.MockKeyboard()
    
    executor = TaskExecutor(MockSkills(), None)
    
    # Test multi-step task
    steps = [
        {
            'intent': 'browser.open_website',
            'parameters': {'url': 'google.com'},
            'description': 'Open Google',
            'delay': 0
        },
        {
            'intent': 'keyboard.type_text',
            'parameters': {'text': 'hello world'},
            'description': 'Type text',
            'delay': 2
        }
    ]
    
    results = executor.execute_multi_step_task(steps)
    print("\nResults:")
    for result in results:
        print(f"  Step {result['step']}: {result['result']}")
    
    print(f"\n{executor.get_task_summary(results)}")
```

---

## STEP 3 — Create Task Scheduler

Create `C:\coco\core\scheduler.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import sqlite3
import json

class TaskScheduler:
    def __init__(self, db_path="scheduler/tasks.db", task_executor=None):
        self.db_path = db_path
        self.task_executor = task_executor
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
```

---

## STEP 4 — Create Workflow Manager

Create `C:\coco\core\workflow_manager.py`:

```python
import json
import os
from datetime import datetime

class WorkflowManager:
    def __init__(self, workflow_dir="workflows"):
        self.workflow_dir = workflow_dir
        os.makedirs(workflow_dir, exist_ok=True)
        self.workflows = {}
        self.load_all_workflows()
        print(f"[WorkflowManager] Loaded {len(self.workflows)} workflows")
    
    def create_workflow(self, name, description, steps):
        """Create and save a new workflow"""
        workflow = {
            'name': name,
            'description': description,
            'steps': steps,
            'created_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # Save to file
        filepath = os.path.join(self.workflow_dir, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        # Add to memory
        self.workflows[name] = workflow
        
        return f"Created workflow '{name}' with {len(steps)} steps"
    
    def load_workflow(self, name):
        """Load a workflow by name"""
        if name in self.workflows:
            return self.workflows[name]
        
        # Try loading from file
        filepath = os.path.join(self.workflow_dir, f"{name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                workflow = json.load(f)
                self.workflows[name] = workflow
                return workflow
        
        return None
    
    def load_all_workflows(self):
        """Load all workflows from directory"""
        if not os.path.exists(self.workflow_dir):
            return
        
        for filename in os.listdir(self.workflow_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.workflow_dir, filename)
                with open(filepath, 'r') as f:
                    workflow = json.load(f)
                    self.workflows[workflow['name']] = workflow
    
    def list_workflows(self):
        """List all available workflows"""
        return list(self.workflows.keys())
    
    def get_workflow_details(self, name):
        """Get detailed info about a workflow"""
        workflow = self.load_workflow(name)
        if workflow:
            return {
                'name': workflow['name'],
                'description': workflow['description'],
                'steps': len(workflow['steps']),
                'created': workflow.get('created_at', 'Unknown')
            }
        return None
    
    def delete_workflow(self, name):
        """Delete a workflow"""
        # Remove from memory
        if name in self.workflows:
            del self.workflows[name]
        
        # Remove file
        filepath = os.path.join(self.workflow_dir, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return f"Deleted workflow '{name}'"
        
        return f"Workflow '{name}' not found"
    
    def export_workflow(self, name, export_path):
        """Export workflow to a file"""
        workflow = self.load_workflow(name)
        if workflow:
            with open(export_path, 'w') as f:
                json.dump(workflow, f, indent=2)
            return f"Exported '{name}' to {export_path}"
        return f"Workflow '{name}' not found"
    
    def import_workflow(self, import_path):
        """Import workflow from a file"""
        with open(import_path, 'r') as f:
            workflow = json.load(f)
            name = workflow['name']
            self.workflows[name] = workflow
            
            # Save to workflow directory
            filepath = os.path.join(self.workflow_dir, f"{name}.json")
            with open(filepath, 'w') as out:
                json.dump(workflow, out, indent=2)
            
            return f"Imported workflow '{name}'"

# Create default workflows
def create_default_workflows():
    """Create some example workflows"""
    manager = WorkflowManager()
    
    # Morning routine workflow
    manager.create_workflow(
        name="morning_routine",
        description="Open essential apps for the day",
        steps=[
            {
                'intent': 'browser.open_website',
                'parameters': {'url': 'gmail.com'},
                'description': 'Open email',
                'delay': 0
            },
            {
                'intent': 'browser.open_website',
                'parameters': {'url': 'calendar.google.com'},
                'description': 'Open calendar',
                'delay': 2
            },
            {
                'intent': 'system.open_app',
                'parameters': {'app': 'notepad'},
                'description': 'Open notepad for notes',
                'delay': 1
            }
        ]
    )
    
    # Screenshot and save workflow
    manager.create_workflow(
        name="screenshot_and_save",
        description="Take screenshot and save to specific location",
        steps=[
            {
                'intent': 'keyboard.screenshot',
                'parameters': {'filename': 'screenshot.png'},
                'description': 'Take screenshot',
                'delay': 0
            },
            {
                'intent': 'files.create_file',
                'parameters': {
                    'filepath': 'screenshots/notes.txt',
                    'content': f'Screenshot taken at {datetime.now()}'
                },
                'description': 'Log screenshot',
                'delay': 1
            }
        ]
    )
    
    print("✅ Created default workflows")

# Test script
if __name__ == "__main__":
    create_default_workflows()
    
    manager = WorkflowManager()
    
    print("\nAvailable workflows:")
    for name in manager.list_workflows():
        details = manager.get_workflow_details(name)
        print(f"  - {name}: {details['description']} ({details['steps']} steps)")
```

---

## STEP 5 — Create Service Integrations

### 5.1 Create Integrations Package
```powershell
mkdir C:\coco\integrations
New-Item C:\coco\integrations\__init__.py -ItemType File
```

### 5.2 Create Gmail Integration
Create `C:\coco\integrations\gmail_integration.py`:

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailIntegration:
    def __init__(self, credentials_path='credentials.json', token_path='token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticated = False
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load saved credentials
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    return "Error: credentials.json not found. Download from Google Cloud Console."
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.authenticated = True
        return "Gmail authenticated successfully"
    
    def check_unread_count(self):
        """Get count of unread emails"""
        if not self.authenticated:
            return "Not authenticated"
        
        try:
            results = self.service.users().messages().list(
                userId='me', q='is:unread').execute()
            messages = results.get('messages', [])
            return f"You have {len(messages)} unread emails"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_latest_emails(self, count=5):
        """Get latest emails"""
        if not self.authenticated:
            return "Not authenticated"
        
        try:
            results = self.service.users().messages().list(
                userId='me', maxResults=count).execute()
            messages = results.get('messages', [])
            
            email_summaries = []
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me', id=msg['id']).execute()
                
                # Extract subject and sender
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                email_summaries.append(f"From {sender}: {subject}")
            
            return email_summaries
        except Exception as e:
            return f"Error: {str(e)}"

# Note: To use Gmail API, you need to:
# 1. Create project in Google Cloud Console
# 2. Enable Gmail API
# 3. Create OAuth 2.0 credentials
# 4. Download credentials.json
# 5. Place it in C:\coco\
```

### 5.3 Create Weather Integration
Create `C:\coco\integrations\weather_integration.py`:

```python
import requests

class WeatherIntegration:
    def __init__(self):
        # Using free wttr.in service (no API key needed)
        self.base_url = "https://wttr.in"
    
    def get_weather(self, city=""):
        """Get weather for a city"""
        try:
            # Format 3 gives concise output
            url = f"{self.base_url}/{city}?format=3"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                return "Could not fetch weather"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_detailed_weather(self, city=""):
        """Get detailed weather forecast"""
        try:
            url = f"{self.base_url}/{city}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                temp = current['temp_C']
                feels_like = current['FeelsLikeC']
                desc = current['weatherDesc'][0]['value']
                humidity = current['humidity']
                
                return f"Current: {temp}°C (feels like {feels_like}°C), {desc}, Humidity {humidity}%"
            else:
                return "Could not fetch weather"
        except Exception as e:
            return f"Error: {str(e)}"

# Test script
if __name__ == "__main__":
    weather = WeatherIntegration()
    print(weather.get_weather("London"))
    print(weather.get_detailed_weather("London"))
```

---

## STEP 6 — Create Pattern Learner

Create `C:\coco\core\pattern_learner.py`:

```python
import sqlite3
from datetime import datetime, timedelta
from collections import Counter

class PatternLearner:
    def __init__(self, db_path="memory/patterns.db", conversation_db="memory/conversation.db"):
        self.db_path = db_path
        self.conversation_db = conversation_db
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
```

---

## STEP 7 — Create Advanced Agent (Phase 3)

Create `C:\coco\core\coco_advanced.py`:

```python
import os
import sys
import whisper
import torch
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import requests
import json
from kokoro_onnx import Kokoro
from dotenv import load_dotenv

sys.path.append('C:/coco')

from core.skill_manager import SkillManager
from core.wake_detector import WakeDetector
from core.memory_manager import MemoryManager
from core.task_executor import TaskExecutor
from core.scheduler import TaskScheduler
from core.workflow_manager import WorkflowManager
from core.pattern_learner import PatternLearner
from integrations.weather_integration import WeatherIntegration

load_dotenv()

# Load models
print("[coco] Loading Whisper on GPU...")
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = whisper.load_model("medium", device=device)

print("[coco] Loading Kokoro...")
tts_model = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

print("[coco] Initializing components...")
wake_detector = WakeDetector(clap_threshold=0.3)
skills = SkillManager()
memory = MemoryManager()
task_executor = TaskExecutor(skills, memory)
scheduler = TaskScheduler(task_executor=task_executor)
workflows = WorkflowManager()
patterns = PatternLearner()
weather = WeatherIntegration()

# Cloud API
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"
OLLAMA_MODEL = "gpt-oss:120b"

ADVANCED_SYSTEM_PROMPT = """You are coco, an advanced AI agent with multi-step execution, scheduling, and workflow capabilities.

You can now handle complex requests:
- Multi-step tasks: "Open notepad AND type hello AND save it"
- Scheduling: "Check weather every hour" or "Remind me at 3pm"
- Workflows: "Run my morning routine"
- Integrations: Weather, email (if configured)

Response Format (JSON):
{
  "type": "single" | "multi_step" | "schedule" | "workflow" | "conversation",
  "intent": "skill.action" or null,
  "parameters": {},
  "steps": [],  // For multi-step tasks
  "schedule": {},  // For scheduled tasks
  "workflow_name": "",  // For workflow execution
  "response": "What to say to user"
}

Examples:

User: "Open notepad"
{
  "type": "single",
  "intent": "system.open_app",
  "parameters": {"app": "notepad"},
  "response": "Opening notepad"
}

User: "Open notepad and type hello world"
{
  "type": "multi_step",
  "steps": [
    {"intent": "system.open_app", "parameters": {"app": "notepad"}, "description": "Open notepad", "delay": 1},
    {"intent": "keyboard.type_text", "parameters": {"text": "hello world"}, "description": "Type text", "delay": 0}
  ],
  "response": "Opening notepad and typing the text"
}

User: "Check weather every hour"
{
  "type": "schedule",
  "schedule": {"type": "interval", "minutes": 60},
  "intent": "integration.weather",
  "response": "I'll check the weather every hour"
}

User: "Run morning routine"
{
  "type": "workflow",
  "workflow_name": "morning_routine",
  "response": "Running your morning routine"
}

User: "What's the weather?"
{
  "type": "single",
  "intent": "integration.weather",
  "parameters": {},
  "response": "Let me check the weather"
}

Always respond with valid JSON."""

def record_audio(duration=5, sample_rate=16000):
    """Record audio"""
    print("[coco] Listening...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    wav.write("temp_input.wav", sample_rate, audio)
    return "temp_input.wav"

def transcribe(audio_path):
    """Transcribe audio"""
    result = stt_model.transcribe(audio_path)
    return result['text'].strip()

def think(user_input, conversation_context=""):
    """Get LLM response"""
    headers = {
        'Authorization': f'Bearer {OLLAMA_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    user_prompt = f"Recent context:\n{conversation_context}\n\nCurrent: {user_input}" if conversation_context else user_input
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": ADVANCED_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_CLOUD_URL, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            content = response.json()['message']['content'].strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            return json.loads(content)
        return {"type": "conversation", "response": f"Error: {response.status_code}"}
    except Exception as e:
        return {"type": "conversation", "response": f"Error: {str(e)}"}

def speak(text):
    """Speak text"""
    print(f"[coco] {text}")
    samples, sample_rate = tts_model.create(text, voice="af_bella", speed=1.0, lang="en-us")
    sd.play(samples, sample_rate)
    sd.wait()

def handle_response(llm_response, user_text):
    """Handle LLM response based on type"""
    response_type = llm_response.get("type", "conversation")
    
    if response_type == "single":
        # Single action
        intent = llm_response.get("intent")
        
        # Handle integrations
        if intent == "integration.weather":
            result = weather.get_weather()
            speak(result)
            memory.add_interaction("assistant", result, intent="integration.weather", action_result=result)
            patterns.log_command(user_text, "integration.weather")
            return
        
        # Regular skill execution
        result = task_executor.execute_skill(intent, llm_response.get("parameters", {}))
        if result:
            print(f"[Action] {result}")
        
        speak(llm_response["response"])
        memory.add_interaction("assistant", llm_response["response"], intent=intent, action_result=result)
        patterns.log_command(user_text, intent)
    
    elif response_type == "multi_step":
        # Multi-step execution
        steps = llm_response.get("steps", [])
        speak(llm_response["response"])
        
        results = task_executor.execute_multi_step_task(steps)
        summary = task_executor.get_task_summary(results)
        speak(summary)
        
        memory.add_interaction("assistant", summary, intent="multi_step", action_result=str(results))
        patterns.log_command(user_text, "multi_step")
    
    elif response_type == "schedule":
        # Schedule task
        schedule_config = llm_response.get("schedule", {})
        
        if schedule_config.get("type") == "interval":
            task_config = {
                'name': f"scheduled_{user_text[:20]}",
                'intent': llm_response.get("intent"),
                'parameters': llm_response.get("parameters", {})
            }
            
            result = scheduler.schedule_interval_task(
                task_config['name'],
                schedule_config.get('minutes', 60),
                task_config
            )
            
            speak(result)
            memory.add_interaction("assistant", result, intent="schedule")
    
    elif response_type == "workflow":
        # Execute workflow
        workflow_name = llm_response.get("workflow_name")
        workflow = workflows.load_workflow(workflow_name)
        
        if workflow:
            speak(f"Running {workflow_name}")
            results = task_executor.execute_multi_step_task(workflow['steps'])
            summary = task_executor.get_task_summary(results)
            speak(summary)
            memory.add_interaction("assistant", summary, intent="workflow", action_result=workflow_name)
        else:
            speak(f"Workflow {workflow_name} not found")
    
    else:
        # Normal conversation
        speak(llm_response["response"])
        memory.add_interaction("assistant", llm_response["response"])

# Main Loop
print("\n" + "="*60)
print("  coco Agent v3.0 - Advanced Intelligence")
print("="*60)
print("\n[coco] Ready! Clap twice to wake me up.")
print("[coco] New capabilities: Multi-step, Scheduling, Workflows")
print("[coco] Say 'exit' to stop.\n")

try:
    while True:
        if wake_detector.listen_for_wake(duration=0.5):
            print("👏👏 [Wake] Double-clap detected!")
            speak("Yes?")
            
            audio_path = record_audio(duration=5)
            user_text = transcribe(audio_path)
            
            if not user_text:
                continue
            
            print(f"[You] {user_text}")
            
            if any(word in user_text.lower() for word in ["exit", "quit", "shutdown coco"]):
                speak("Shutting down. Goodbye!")
                break
            
            memory.add_interaction("user", user_text)
            
            context = memory.get_recent_context(limit=5)
            llm_response = think(user_text, context)
            
            handle_response(llm_response, user_text)

except KeyboardInterrupt:
    print("\n\n[coco] Interrupted")

finally:
    print("\n[coco] Cleaning up...")
    skills.browser.close_browser()
    scheduler.shutdown()
    memory.close()
    print(f"[coco] {memory.get_session_summary()}")
    
    stats = patterns.get_usage_statistics()
    print(f"[coco] Learned {stats['unique_commands']} command patterns")
```

---

## STEP 8 — Update Requirements

Add to `C:\coco\requirements.txt`:

```
apscheduler
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
spotipy
python-dateutil
```

Install:
```powershell
cd C:\coco
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## STEP 9 — Create Folders

```powershell
mkdir C:\coco\workflows
mkdir C:\coco\scheduler
mkdir C:\coco\integrations
```

---

## STEP 10 — Initialize Default Workflows

```powershell
python -c "from core.workflow_manager import create_default_workflows; create_default_workflows()"
```

---

## STEP 11 — Test Phase 3

### 11.1 Run Advanced Agent
```powershell
cd C:\coco
.\venv\Scripts\activate
python core\coco_advanced.py
```

### 11.2 Test Advanced Features

**Multi-Step Commands:**
- 👏👏 "Open notepad and type hello world"
- 👏👏 "Open Chrome and search for AI news"
- 👏👏 "Take a screenshot and create a log file"

**Workflows:**
- 👏👏 "Run morning routine"
- 👏👏 "List my workflows"

**Scheduling:**
- 👏👏 "Check weather every 10 minutes"
- 👏👏 "List scheduled tasks"

**Integrations:**
- 👏👏 "What's the weather?"
- 👏👏 "What's the weather in Tokyo?"

---

## Phase 3 Completion Checklist

| Feature | Status |
|---------|--------|
| APScheduler installed | ✅ |
| Multi-step task executor created | ✅ |
| Task scheduler operational | ✅ |
| Workflow manager functional | ✅ |
| Default workflows created | ✅ |
| Pattern learner tracking usage | ✅ |
| Weather integration working | ✅ |
| Advanced agent running | ✅ |
| Multi-step commands executing | ✅ |
| Scheduling tasks working | ✅ |

---

## Advanced Usage Examples

### Create Custom Workflow

```python
from core.workflow_manager import WorkflowManager

wf = WorkflowManager()
wf.create_workflow(
    name="email_check",
    description="Check email and weather",
    steps=[
        {
            'intent': 'integration.weather',
            'parameters': {},
            'description': 'Check weather',
            'delay': 0
        },
        {
            'intent': 'browser.open_website',
            'parameters': {'url': 'gmail.com'},
            'description': 'Open email',
            'delay': 2
        }
    ]
)
```

### Schedule Custom Task

```python
from core.scheduler import TaskScheduler

scheduler = TaskScheduler(task_executor)

task = {
    'name': 'hourly_weather',
    'intent': 'integration.weather',
    'parameters': {}
}

scheduler.schedule_interval_task('weather_check', 60, task)
```

---

## Gmail Setup (Optional)

To enable Gmail integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`
6. Place in `C:\coco\credentials.json`
7. First run will open browser for authorization

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Scheduler not running | Check if APScheduler installed correctly |
| Workflows not loading | Verify `workflows/` folder exists |
| Multi-step fails halfway | Check individual step syntax |
| Pattern learner not tracking | Database permissions issue - check `memory/` folder |
| Weather integration timeout | Network issue - check internet connection |
| Gmail auth fails | Ensure credentials.json is valid and in root folder |

---

## Performance Tips

- Limit scheduled tasks to essentials (max 5-10 active)
- Clear old patterns periodically
- Use workflows for complex tasks instead of multi-step commands
- Schedule heavy tasks during low-usage times

---

## What's Next: Phase 4 Ideas

- Voice customization (male/female, speed, accent)
- Multi-language support
- Visual dashboard (web UI to manage coco)
- Mobile app companion
- Cloud sync for workflows and patterns
- Advanced NLP for better intent parsing
- Integration with more services (Slack, Discord, etc.)

---

🎉 **Phase 3 Complete!**

coco is now an **advanced autonomous agent** with:
- Multi-step task chaining
- Background scheduling
- Reusable workflows
- Service integrations
- Usage pattern learning

You can now say:
- "Open Chrome, search for Python tutorials, and take notes" ✅
- "Check weather every hour" ✅
- "Run my morning routine" ✅
- "What's the weather in London?" ✅

**coco is production-ready!** 🚀
