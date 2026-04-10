# coco — Phase 2: System Automation & Skills
### Full Agent Capabilities - Detailed Build Instructions

---

## Prerequisites

Before starting Phase 2, you MUST have completed Phase 1:
- ✅ coco core loop working (STT → Cloud LLM → TTS)
- ✅ Whisper transcribing voice correctly
- ✅ Ollama Cloud API responding
- ✅ Kokoro speaking responses
- ✅ Virtual environment active and working

---

## What Phase 2 Adds

After Phase 2, coco will be able to:
- 🌐 **Browser Automation** - Open websites, fill forms, click buttons, scrape data
- 💻 **System Control** - Open/close apps, manage files, take screenshots
- ⌨️ **Keyboard & Mouse** - Type text, move mouse, click anywhere on screen
- 📸 **Screen Reading** - Read text from screen, analyze what's visible
- 📁 **File Operations** - Create, read, move, delete files and folders
- 🎯 **Task Automation** - Chain multiple actions together
- 🧠 **Skills System** - Modular capabilities coco can learn and use

---

## Architecture Overview

```
coco/
├── core/
│   ├── coco_core.py          # Main loop (Phase 1)
│   ├── coco_agent.py          # Agent with skills (Phase 2)
│   └── skill_manager.py       # Skills orchestrator
├── skills/
│   ├── __init__.py
│   ├── browser_skill.py       # Playwright automation
│   ├── system_skill.py        # Windows control
│   ├── keyboard_skill.py      # Keyboard/mouse control
│   ├── screen_skill.py        # Screen reading/OCR
│   └── file_skill.py          # File operations
├── stt/
├── tts/
├── brain/
└── memory/
    └── task_history.db        # Log of executed tasks
```

---

## STEP 1 — Install Playwright (Browser Automation)

### 1.1 Activate Virtual Environment
```powershell
cd C:\coco
.\venv\Scripts\activate
```

### 1.2 Install Playwright
```powershell
pip install playwright
pip install playwright-stealth
```

### 1.3 Install Browser Drivers
This downloads Chromium, Firefox, and WebKit browsers:
```powershell
playwright install
```

This takes ~5 minutes and downloads ~500MB.

### 1.4 Test Playwright
Create `C:\coco\skills\test_playwright.py`:

```python
from playwright.sync_api import sync_playwright
import time

print("[Test] Starting Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    print("[Test] Opening Google...")
    page.goto("https://www.google.com")
    
    print("[Test] Searching for 'coco AI assistant'...")
    page.fill('textarea[name="q"]', 'coco AI assistant')
    page.press('textarea[name="q"]', 'Enter')
    
    time.sleep(3)
    print("[Test] Search complete!")
    
    browser.close()
    print("[Test] ✅ Playwright working!")
```

Run it:
```powershell
python skills\test_playwright.py
```

Expected: A browser window opens, searches Google, then closes. ✅

---

## STEP 2 — Install System Control Libraries

### 2.1 Install PyAutoGUI (Keyboard & Mouse Control)
```powershell
pip install pyautogui
pip install pillow
```

### 2.2 Install psutil (Process Management)
```powershell
pip install psutil
```

### 2.3 Install pygetwindow (Window Management - Windows Only)
```powershell
pip install pygetwindow
```

### 2.4 Test PyAutoGUI
Create `C:\coco\skills\test_system.py`:

```python
import pyautogui
import time

print("[Test] Moving mouse to center of screen...")
screen_width, screen_height = pyautogui.size()
pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=1)

print("[Test] Taking screenshot...")
screenshot = pyautogui.screenshot()
screenshot.save("test_screenshot.png")
print("[Test] Screenshot saved as test_screenshot.png")

print("[Test] ✅ System control working!")
```

Run it:
```powershell
python skills\test_system.py
```

Expected: Mouse moves to center, screenshot taken. ✅

---

## STEP 3 — Install OCR (Screen Reading)

### 3.1 Install EasyOCR
```powershell
pip install easyocr
pip install opencv-python
```

First run downloads ~500MB of OCR models.

### 3.2 Test OCR
Create `C:\coco\skills\test_ocr.py`:

```python
import easyocr
import pyautogui

print("[Test] Loading OCR model (this takes ~30 seconds first time)...")
reader = easyocr.Reader(['en'], gpu=False)

print("[Test] Taking screenshot...")
screenshot = pyautogui.screenshot()
screenshot.save("temp_screen.png")

print("[Test] Reading text from screen...")
results = reader.readtext("temp_screen.png")

print("[Test] Text found on screen:")
for detection in results[:5]:  # Show first 5 results
    print(f"  - {detection[1]}")

print("[Test] ✅ OCR working!")
```

Run it:
```powershell
python skills\test_ocr.py
```

Expected: Shows text detected on your screen. ✅

---

## STEP 4 — Create Skills Framework

### 4.1 Create Skills Package
```powershell
New-Item C:\coco\skills\__init__.py -ItemType File
```

### 4.2 Create Browser Skill
Create `C:\coco\skills\browser_skill.py`:

```python
from playwright.sync_api import sync_playwright
import time

class BrowserSkill:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        
    def start_browser(self, headless=False):
        """Launch browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()
        return "Browser started"
    
    def open_website(self, url):
        """Open a website"""
        if not self.page:
            self.start_browser()
        
        if not url.startswith('http'):
            url = 'https://' + url
            
        self.page.goto(url, timeout=30000)
        return f"Opened {url}"
    
    def search_google(self, query):
        """Search on Google"""
        self.open_website("https://www.google.com")
        self.page.fill('textarea[name="q"]', query)
        self.page.press('textarea[name="q"]', 'Enter')
        time.sleep(2)
        return f"Searched Google for: {query}"
    
    def click_element(self, selector):
        """Click an element by CSS selector"""
        if not self.page:
            return "No browser open"
        self.page.click(selector)
        return f"Clicked {selector}"
    
    def type_text(self, selector, text):
        """Type text into an element"""
        if not self.page:
            return "No browser open"
        self.page.fill(selector, text)
        return f"Typed text into {selector}"
    
    def get_page_title(self):
        """Get current page title"""
        if not self.page:
            return "No browser open"
        return self.page.title()
    
    def get_page_text(self):
        """Get visible text from page"""
        if not self.page:
            return "No browser open"
        return self.page.inner_text('body')
    
    def take_screenshot(self, filename="screenshot.png"):
        """Take screenshot of current page"""
        if not self.page:
            return "No browser open"
        self.page.screenshot(path=filename)
        return f"Screenshot saved as {filename}"
    
    def close_browser(self):
        """Close the browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.browser = None
        self.page = None
        self.playwright = None
        return "Browser closed"

# Test usage
if __name__ == "__main__":
    browser = BrowserSkill()
    print(browser.start_browser())
    print(browser.search_google("AI automation"))
    time.sleep(3)
    print(browser.close_browser())
```

### 4.3 Create System Skill
Create `C:\coco\skills\system_skill.py`:

```python
import subprocess
import os
import psutil
import pygetwindow as gw
import time

class SystemSkill:
    def __init__(self):
        pass
    
    def open_application(self, app_name):
        """Open an application by name"""
        apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'edge': 'msedge.exe',
            'chrome': 'chrome.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
        }
        
        app_lower = app_name.lower()
        
        if app_lower in apps:
            try:
                subprocess.Popen(apps[app_lower])
                return f"Opened {app_name}"
            except Exception as e:
                return f"Error opening {app_name}: {str(e)}"
        else:
            # Try to run as-is
            try:
                subprocess.Popen(app_name)
                return f"Opened {app_name}"
            except Exception as e:
                return f"Could not open {app_name}: {str(e)}"
    
    def close_application(self, app_name):
        """Close an application by name"""
        app_lower = app_name.lower()
        closed = False
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if app_lower in proc_name:
                    proc.terminate()
                    closed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if closed:
            return f"Closed {app_name}"
        else:
            return f"{app_name} not found or already closed"
    
    def list_running_apps(self):
        """List all running applications"""
        apps = []
        for proc in psutil.process_iter(['name']):
            try:
                apps.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Remove duplicates and sort
        unique_apps = sorted(set(apps))
        return unique_apps[:20]  # Return first 20
    
    def get_active_window(self):
        """Get the title of the active window"""
        try:
            active = gw.getActiveWindow()
            if active:
                return active.title
            return "No active window"
        except:
            return "Could not get active window"
    
    def minimize_window(self, title):
        """Minimize a window by title"""
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                windows[0].minimize()
                return f"Minimized {title}"
            return f"Window '{title}' not found"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def maximize_window(self, title):
        """Maximize a window by title"""
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                windows[0].maximize()
                return f"Maximized {title}"
            return f"Window '{title}' not found"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def shutdown_system(self):
        """Shutdown the computer"""
        os.system("shutdown /s /t 10")
        return "System will shutdown in 10 seconds"
    
    def restart_system(self):
        """Restart the computer"""
        os.system("shutdown /r /t 10")
        return "System will restart in 10 seconds"

# Test usage
if __name__ == "__main__":
    system = SystemSkill()
    print(system.open_application("notepad"))
    time.sleep(2)
    print(system.close_application("notepad"))
```

### 4.4 Create Keyboard Skill
Create `C:\coco\skills\keyboard_skill.py`:

```python
import pyautogui
import time

class KeyboardSkill:
    def __init__(self):
        # Safety feature - move mouse to corner to abort
        pyautogui.FAILSAFE = True
        # Pause between actions
        pyautogui.PAUSE = 0.1
    
    def type_text(self, text, interval=0.05):
        """Type text with optional interval between keys"""
        pyautogui.write(text, interval=interval)
        return f"Typed: {text}"
    
    def press_key(self, key):
        """Press a single key"""
        pyautogui.press(key)
        return f"Pressed {key}"
    
    def press_hotkey(self, *keys):
        """Press a combination of keys (e.g., ctrl+c)"""
        pyautogui.hotkey(*keys)
        return f"Pressed {'+'.join(keys)}"
    
    def click_at(self, x, y, clicks=1, button='left'):
        """Click at specific coordinates"""
        pyautogui.click(x, y, clicks=clicks, button=button)
        return f"Clicked at ({x}, {y})"
    
    def move_mouse(self, x, y, duration=0.5):
        """Move mouse to coordinates"""
        pyautogui.moveTo(x, y, duration=duration)
        return f"Moved mouse to ({x}, {y})"
    
    def get_mouse_position(self):
        """Get current mouse position"""
        x, y = pyautogui.position()
        return f"Mouse at ({x}, {y})"
    
    def take_screenshot(self, filename="screenshot.png"):
        """Take screenshot"""
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved as {filename}"
    
    def get_screen_size(self):
        """Get screen dimensions"""
        width, height = pyautogui.size()
        return f"Screen size: {width}x{height}"

# Test usage
if __name__ == "__main__":
    kb = KeyboardSkill()
    print(kb.get_screen_size())
    print(kb.get_mouse_position())
```

### 4.5 Create Screen Reading Skill
Create `C:\coco\skills\screen_skill.py`:

```python
import easyocr
import pyautogui
import os

class ScreenSkill:
    def __init__(self):
        # Load OCR model (English)
        print("[ScreenSkill] Loading OCR model...")
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("[ScreenSkill] OCR ready")
    
    def read_screen(self):
        """Read all text from current screen"""
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save("temp_screen.png")
        
        # Read text
        results = self.reader.readtext("temp_screen.png")
        
        # Extract text only
        text_list = [detection[1] for detection in results]
        
        # Clean up
        os.remove("temp_screen.png")
        
        return " ".join(text_list) if text_list else "No text found on screen"
    
    def read_region(self, x, y, width, height):
        """Read text from specific screen region"""
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save("temp_region.png")
        
        results = self.reader.readtext("temp_region.png")
        text_list = [detection[1] for detection in results]
        
        os.remove("temp_region.png")
        
        return " ".join(text_list) if text_list else "No text found in region"

# Test usage
if __name__ == "__main__":
    screen = ScreenSkill()
    print(screen.read_screen())
```

### 4.6 Create File Operations Skill
Create `C:\coco\skills\file_skill.py`:

```python
import os
import shutil

class FileSkill:
    def __init__(self):
        pass
    
    def create_file(self, filepath, content=""):
        """Create a new file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Created file: {filepath}"
        except Exception as e:
            return f"Error creating file: {str(e)}"
    
    def read_file(self, filepath):
        """Read file contents"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def delete_file(self, filepath):
        """Delete a file"""
        try:
            os.remove(filepath)
            return f"Deleted file: {filepath}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
    
    def copy_file(self, source, destination):
        """Copy a file"""
        try:
            shutil.copy2(source, destination)
            return f"Copied {source} to {destination}"
        except Exception as e:
            return f"Error copying file: {str(e)}"
    
    def move_file(self, source, destination):
        """Move a file"""
        try:
            shutil.move(source, destination)
            return f"Moved {source} to {destination}"
        except Exception as e:
            return f"Error moving file: {str(e)}"
    
    def create_folder(self, folderpath):
        """Create a new folder"""
        try:
            os.makedirs(folderpath, exist_ok=True)
            return f"Created folder: {folderpath}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"
    
    def list_files(self, folderpath="."):
        """List files in a folder"""
        try:
            files = os.listdir(folderpath)
            return files
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    def file_exists(self, filepath):
        """Check if file exists"""
        return os.path.exists(filepath)

# Test usage
if __name__ == "__main__":
    files = FileSkill()
    print(files.create_file("test.txt", "Hello from coco!"))
    print(files.read_file("test.txt"))
```

---

## STEP 5 — Create Skill Manager

Create `C:\coco\core\skill_manager.py`:

```python
import sys
sys.path.append('C:/coco')

from skills.browser_skill import BrowserSkill
from skills.system_skill import SystemSkill
from skills.keyboard_skill import KeyboardSkill
from skills.screen_skill import ScreenSkill
from skills.file_skill import FileSkill

class SkillManager:
    def __init__(self):
        print("[SkillManager] Initializing skills...")
        self.browser = BrowserSkill()
        self.system = SystemSkill()
        self.keyboard = KeyboardSkill()
        self.screen = ScreenSkill()  # This takes ~30 seconds to load OCR
        self.files = FileSkill()
        print("[SkillManager] All skills loaded ✅")
    
    def execute_command(self, intent, parameters):
        """Execute a command based on intent"""
        
        # Browser commands
        if intent == "open_website":
            return self.browser.open_website(parameters.get('url'))
        elif intent == "search_google":
            return self.browser.search_google(parameters.get('query'))
        elif intent == "close_browser":
            return self.browser.close_browser()
        
        # System commands
        elif intent == "open_app":
            return self.system.open_application(parameters.get('app'))
        elif intent == "close_app":
            return self.system.close_application(parameters.get('app'))
        elif intent == "list_apps":
            apps = self.system.list_running_apps()
            return f"Running: {', '.join(apps[:10])}"
        
        # Keyboard commands
        elif intent == "type_text":
            return self.keyboard.type_text(parameters.get('text'))
        elif intent == "press_key":
            return self.keyboard.press_key(parameters.get('key'))
        elif intent == "screenshot":
            return self.keyboard.take_screenshot(parameters.get('filename', 'screenshot.png'))
        
        # Screen reading
        elif intent == "read_screen":
            return self.screen.read_screen()
        
        # File operations
        elif intent == "create_file":
            return self.files.create_file(parameters.get('filepath'), parameters.get('content', ''))
        elif intent == "read_file":
            return self.files.read_file(parameters.get('filepath'))
        elif intent == "list_files":
            return str(self.files.list_files(parameters.get('folder', '.')))
        
        else:
            return f"Unknown intent: {intent}"
    
    def parse_natural_command(self, command):
        """Parse natural language command into intent and parameters"""
        command_lower = command.lower()
        
        # Browser patterns
        if "open" in command_lower and any(x in command_lower for x in ["website", "site", ".com", "http"]):
            # Extract URL
            words = command.split()
            url = next((w for w in words if '.com' in w or 'http' in w), None)
            if url:
                return ("open_website", {"url": url})
        
        elif "search" in command_lower and "google" in command_lower:
            # Extract query after "search" or "for"
            if "for" in command_lower:
                query = command_lower.split("for", 1)[1].strip()
            else:
                query = command_lower.replace("search", "").replace("google", "").strip()
            return ("search_google", {"query": query})
        
        elif "close browser" in command_lower:
            return ("close_browser", {})
        
        # System patterns
        elif "open" in command_lower and any(x in command_lower for x in ["notepad", "calculator", "paint", "chrome", "edge"]):
            app = next((x for x in ["notepad", "calculator", "paint", "chrome", "edge"] if x in command_lower), None)
            return ("open_app", {"app": app})
        
        elif "close" in command_lower:
            words = command_lower.split()
            app = words[-1] if words else ""
            return ("close_app", {"app": app})
        
        elif "what" in command_lower and "running" in command_lower:
            return ("list_apps", {})
        
        # Keyboard patterns
        elif "type" in command_lower:
            text = command.replace("type", "", 1).strip()
            return ("type_text", {"text": text})
        
        elif "screenshot" in command_lower:
            return ("screenshot", {})
        
        # Screen reading
        elif "read screen" in command_lower or "what's on screen" in command_lower:
            return ("read_screen", {})
        
        # File patterns
        elif "create file" in command_lower:
            return ("create_file", {"filepath": "created_file.txt", "content": "Created by coco"})
        
        elif "list files" in command_lower:
            return ("list_files", {"folder": "."})
        
        return (None, {})

# Test usage
if __name__ == "__main__":
    manager = SkillManager()
    
    test_commands = [
        "open google.com",
        "search google for AI automation",
        "open notepad",
        "type hello world",
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        intent, params = manager.parse_natural_command(cmd)
        if intent:
            result = manager.execute_command(intent, params)
            print(f"Result: {result}")
        else:
            print("Could not parse command")
```

---

## STEP 6 — Integrate Skills with coco Agent

Create `C:\coco\core\coco_agent.py`:

```python
import os
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import requests
from kokoro_onnx import Kokoro
import soundfile as sf
from dotenv import load_dotenv
from skill_manager import SkillManager

# Load environment variables
load_dotenv()

# Load models
print("[coco] Loading Whisper...")
stt_model = whisper.load_model("medium")

print("[coco] Loading Kokoro...")
tts_model = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

print("[coco] Loading skills (this takes ~30 seconds)...")
skills = SkillManager()

# Cloud API Configuration
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"
OLLAMA_MODEL = "gpt-oss:120b"

SYSTEM_PROMPT = """You are coco, a powerful AI agent with system control capabilities.

You can:
- Open and close applications
- Control the web browser
- Type text and control keyboard/mouse
- Read text from the screen
- Manage files and folders
- Search the web
- Take screenshots

When the user asks you to do something, first determine if it requires a skill action.
If yes, respond with ONLY the action in this format:
ACTION: intent_name | parameter1: value1 | parameter2: value2

Examples:
User: "Open notepad"
You: ACTION: open_app | app: notepad

User: "Search google for AI news"
You: ACTION: search_google | query: AI news

User: "What's the weather like?"
You: No action needed. Just respond normally about checking weather.

For normal conversation, respond naturally without ACTION prefix.
Keep responses concise."""

def record_audio(duration=5, sample_rate=16000):
    print("[coco] Listening...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    wav.write("temp_input.wav", sample_rate, audio)
    return "temp_input.wav"

def transcribe(audio_path):
    result = stt_model.transcribe(audio_path)
    return result['text'].strip()

def think(user_input):
    headers = {
        'Authorization': f'Bearer {OLLAMA_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_CLOUD_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['message']['content'].strip()
        else:
            return f"Error: Cloud API returned {response.status_code}"
    except Exception as e:
        return f"Error connecting to cloud: {str(e)}"

def speak(text):
    print(f"[coco] {text}")
    samples, sample_rate = tts_model.create(text, voice="af_bella", speed=1.0, lang="en-us")
    sd.play(samples, sample_rate)
    sd.wait()

def execute_action(response):
    """Check if response contains an action and execute it"""
    if response.startswith("ACTION:"):
        # Parse action
        action_part = response.replace("ACTION:", "").strip()
        parts = [p.strip() for p in action_part.split("|")]
        
        intent = parts[0]
        parameters = {}
        
        for part in parts[1:]:
            if ":" in part:
                key, value = part.split(":", 1)
                parameters[key.strip()] = value.strip()
        
        # Execute via skill manager
        result = skills.execute_command(intent, parameters)
        return True, result
    
    return False, None

# Main Loop
print("[coco] Agent ready. Starting interaction loop...")
speak("coco agent is ready. I can now control your system. What would you like me to do?")

while True:
    audio_path = record_audio(duration=5)
    user_text = transcribe(audio_path)

    if not user_text:
        continue

    print(f"[You] {user_text}")

    if any(word in user_text.lower() for word in ["exit", "quit", "shutdown coco", "stop"]):
        speak("Shutting down coco agent. Goodbye.")
        skills.browser.close_browser()  # Clean up
        break

    # Get response from LLM
    response = think(user_text)
    
    # Check if it's an action
    is_action, action_result = execute_action(response)
    
    if is_action:
        # Action was executed
        speak(action_result)
    else:
        # Normal conversation
        speak(response)
```

---

## STEP 7 — Update Requirements

Update `C:\coco\requirements.txt`:

```
openai-whisper
sounddevice
scipy
numpy
requests
kokoro-onnx
soundfile
pyaudio
huggingface_hub
python-dotenv
playwright
playwright-stealth
pyautogui
pillow
psutil
pygetwindow
easyocr
opencv-python
```

Install all:
```powershell
cd C:\coco
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

---

## STEP 8 — Test the Agent

### 8.1 Run coco Agent
```powershell
cd C:\coco
.\venv\Scripts\activate
python core\coco_agent.py
```

### 8.2 Test Commands

Try these voice commands:

**Browser:**
- "Open google.com"
- "Search google for artificial intelligence"
- "Close the browser"

**System:**
- "Open notepad"
- "Open calculator"
- "Close notepad"
- "What apps are running"

**Keyboard:**
- "Type hello world"
- "Take a screenshot"

**Screen:**
- "Read what's on the screen"

**Files:**
- "List files in this folder"
- "Create a file called test.txt"

**Conversation:**
- "What's 25 times 4" (should respond normally, no action)
- "Tell me a joke" (should respond normally)

---

## STEP 9 — Create Quick Launch Script

Create `C:\coco\run_agent.bat`:

```batch
@echo off
cd C:\coco
call venv\Scripts\activate
echo.
echo ========================================
echo      coco Agent - System Control
echo ========================================
echo.
python core\coco_agent.py
pause
```

Now you can just double-click `run_agent.bat` to start coco!

---

## Phase 2 Completion Checklist

| Task | Status |
|------|--------|
| Playwright installed and tested | ✅ |
| Browser automation working | ✅ |
| PyAutoGUI installed and tested | ✅ |
| System control working | ✅ |
| OCR installed and tested | ✅ |
| Screen reading working | ✅ |
| All skill files created | ✅ |
| Skill manager working | ✅ |
| Agent integrated with skills | ✅ |
| Voice commands executing actions | ✅ |
| Full system control achieved | ✅ |

---

## Advanced Usage

### Custom Skills

To add your own skill:

1. Create `C:\coco\skills\my_skill.py`
2. Define skill class with methods
3. Import in `skill_manager.py`
4. Add to `SkillManager.__init__()`
5. Add intent parsing in `parse_natural_command()`
6. Add execution in `execute_command()`

### Example: Weather Skill

```python
# skills/weather_skill.py
import requests

class WeatherSkill:
    def get_weather(self, city):
        # Use free weather API
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url)
        return response.text
```

Then integrate it in skill_manager.py.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright browser doesn't open | Run `playwright install` again |
| OCR taking too long | First load is slow (~30s), subsequent calls are fast |
| PyAutoGUI not clicking correctly | Check screen scaling in Windows display settings |
| "Access Denied" errors | Run as administrator for system control |
| Skills not loading | Make sure you're in the venv |

---

## Safety Notes

⚠️ **Important:**
- coco can control your entire system - use responsibly
- Test new commands in a safe environment first
- Browser automation works best in headless=False mode initially
- OCR requires good screen contrast to read text accurately
- System shutdown commands have 10-second delay for safety

---

## Next: Phase 3 Preview

Phase 3 will add:
- Wake word detection ("Hey coco")
- Conversation memory (remember past interactions)
- Task scheduling (run tasks at specific times)
- Custom automation scripts
- Integration with more services
- Advanced error handling and recovery

🎉 **Congratulations! coco is now a full system automation agent!**
