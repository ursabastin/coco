# coco — Phase 2.5: Essential Refinements
### Wake Detection + Memory + GPU Acceleration + Smart Parsing

---

## What Phase 2.5 Fixes

Phase 2 gave coco powerful skills but left critical usability issues:

**Problems Fixed in Phase 2.5:**
- ❌ No wake detection → Always listening = annoying
- ❌ No memory → Forgets everything instantly
- ❌ Whisper on CPU → 5-10 second delays
- ❌ Fragile parsing → "Could you open notepad?" breaks
- ❌ No error recovery → One failure = crash

**After Phase 2.5:**
- ✅ **Double-clap to wake** → Natural, language-free activation
- ✅ **Conversation memory** → Remembers context, can reference "it"
- ✅ **GPU-accelerated Whisper** → 5-10x faster (1-2 seconds)
- ✅ **Structured LLM parsing** → Robust intent extraction
- ✅ **Graceful error handling** → Recovers from failures

---

## Prerequisites

Before starting Phase 2.5, you must have:
- ✅ Phase 1 complete (STT → LLM → TTS working)
- ✅ Phase 2 complete (Skills framework functional)
- ✅ RTX 3050 GPU available
- ✅ Virtual environment active

---

## Architecture Changes

```
coco/
├── core/
│   ├── coco_agent.py          # Phase 2 version
│   ├── coco_refined.py        # NEW: Phase 2.5 agent
│   ├── skill_manager.py       # Same from Phase 2
│   ├── wake_detector.py       # NEW: Double-clap detection
│   └── memory_manager.py      # NEW: Conversation memory
├── memory/
│   └── conversation.db        # NEW: SQLite database
├── skills/                     # Same from Phase 2
├── stt/
├── tts/
└── brain/
```

---

## STEP 1 — Install CUDA for GPU Acceleration

### 1.1 Check GPU Compatibility
```powershell
nvidia-smi
```

You should see your RTX 3050 listed. ✅

### 1.2 Install PyTorch with CUDA Support
```powershell
cd C:\coco
.\venv\Scripts\activate
```

**Uninstall CPU-only PyTorch first:**
```powershell
pip uninstall torch torchvision torchaudio
```

**Install GPU-enabled PyTorch:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

This downloads ~2GB. Wait for completion.

### 1.3 Verify GPU Detection
Create `C:\coco\brain\test_gpu.py`:

```python
import torch
import whisper

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
    
    # Test Whisper on GPU
    print("\nLoading Whisper on GPU...")
    model = whisper.load_model("medium", device="cuda")
    print("✅ Whisper loaded on GPU!")
else:
    print("❌ CUDA not available - Whisper will use CPU")
```

Run it:
```powershell
python brain\test_gpu.py
```

Expected output:
```
CUDA available: True
GPU device: NVIDIA GeForce RTX 3050 Laptop GPU
✅ Whisper loaded on GPU!
```

If you see this → ✅ GPU acceleration ready!

---

## STEP 2 — Implement Double-Clap Wake Detection

### 2.1 Install Audio Analysis Library
```powershell
pip install librosa
```

### 2.2 Create Wake Detector
Create `C:\coco\core\wake_detector.py`:

```python
import numpy as np
import sounddevice as sd
import time

class WakeDetector:
    def __init__(self, 
                 clap_threshold=0.3,      # Amplitude threshold for clap detection
                 clap_gap_min=0.1,        # Minimum gap between claps (seconds)
                 clap_gap_max=0.6,        # Maximum gap between claps (seconds)
                 sample_rate=16000):
        
        self.clap_threshold = clap_threshold
        self.clap_gap_min = clap_gap_min
        self.clap_gap_max = clap_gap_max
        self.sample_rate = sample_rate
        
        # Circular buffer for continuous audio monitoring
        self.buffer_duration = 2.0  # Monitor last 2 seconds
        self.buffer_size = int(self.buffer_duration * self.sample_rate)
        self.audio_buffer = np.zeros(self.buffer_size)
        
        print(f"[WakeDetector] Double-clap detection ready")
        print(f"[WakeDetector] Clap threshold: {clap_threshold}")
        print(f"[WakeDetector] Gap range: {clap_gap_min}-{clap_gap_max}s")
    
    def detect_clap(self, audio_chunk):
        """Detect if audio chunk contains a clap (sudden loud sound)"""
        # Calculate RMS (root mean square) amplitude
        rms = np.sqrt(np.mean(audio_chunk**2))
        return rms > self.clap_threshold
    
    def find_claps_in_buffer(self):
        """Find clap timestamps in the audio buffer"""
        # Split buffer into small chunks (50ms each)
        chunk_size = int(0.05 * self.sample_rate)
        num_chunks = len(self.audio_buffer) // chunk_size
        
        clap_times = []
        
        for i in range(num_chunks):
            start = i * chunk_size
            end = start + chunk_size
            chunk = self.audio_buffer[start:end]
            
            if self.detect_clap(chunk):
                time_offset = i * 0.05  # Convert chunk index to time
                clap_times.append(time_offset)
        
        return clap_times
    
    def is_double_clap(self, clap_times):
        """Check if clap pattern matches double-clap"""
        if len(clap_times) < 2:
            return False
        
        # Check for two claps with proper gap
        for i in range(len(clap_times) - 1):
            gap = clap_times[i + 1] - clap_times[i]
            if self.clap_gap_min <= gap <= self.clap_gap_max:
                return True
        
        return False
    
    def listen_for_wake(self, duration=2.0):
        """Listen for double-clap wake signal"""
        # Record audio chunk
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        # Update circular buffer
        audio_flat = audio.flatten()
        self.audio_buffer = np.roll(self.audio_buffer, -len(audio_flat))
        self.audio_buffer[-len(audio_flat):] = audio_flat
        
        # Find claps in buffer
        clap_times = self.find_claps_in_buffer()
        
        # Check for double-clap pattern
        if self.is_double_clap(clap_times):
            return True
        
        return False
    
    def calibrate(self):
        """Help user calibrate clap threshold"""
        print("\n[WakeDetector] Calibration Mode")
        print("We'll measure your clap volume to set the right threshold.")
        print("\nWhen ready, clap TWICE with ~0.3 seconds between claps.")
        input("Press Enter when ready...")
        
        print("\nListening for 3 seconds... CLAP CLAP NOW!")
        audio = sd.rec(
            int(3 * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        # Find max amplitude
        audio_flat = audio.flatten()
        
        # Split into 50ms chunks and find max RMS
        chunk_size = int(0.05 * self.sample_rate)
        num_chunks = len(audio_flat) // chunk_size
        
        max_rms = 0
        for i in range(num_chunks):
            start = i * chunk_size
            end = start + chunk_size
            chunk = audio_flat[start:end]
            rms = np.sqrt(np.mean(chunk**2))
            if rms > max_rms:
                max_rms = rms
        
        # Set threshold to 70% of max clap volume
        suggested_threshold = max_rms * 0.7
        
        print(f"\n[WakeDetector] Detected clap volume: {max_rms:.3f}")
        print(f"[WakeDetector] Suggested threshold: {suggested_threshold:.3f}")
        print(f"\nRecommendation: Set clap_threshold={suggested_threshold:.2f} in wake_detector.py")
        
        return suggested_threshold

# Test script
if __name__ == "__main__":
    detector = WakeDetector()
    
    # Calibration mode
    print("\nDo you want to calibrate? (y/n)")
    if input().lower() == 'y':
        detector.calibrate()
        print("\nRestarting with default settings for testing...")
    
    print("\n[Test] Listening for double-clap...")
    print("[Test] Clap twice quickly to wake coco!")
    print("[Test] Press Ctrl+C to stop\n")
    
    try:
        while True:
            if detector.listen_for_wake(duration=0.5):
                print("✅ DOUBLE-CLAP DETECTED! coco would wake up now.")
                time.sleep(2)  # Cooldown
    except KeyboardInterrupt:
        print("\n[Test] Stopped")
```

### 2.3 Test Wake Detection
```powershell
python core\wake_detector.py
```

**First Time:**
1. Type `y` for calibration
2. Press Enter
3. Clap twice when prompted
4. Note the suggested threshold
5. Update `clap_threshold` in the code if needed

**Then test:**
- Clap twice quickly → Should see "✅ DOUBLE-CLAP DETECTED!"
- Single clap → Should not trigger
- Claps too far apart → Should not trigger

If working → ✅ Wake detection ready!

---

## STEP 3 — Implement Conversation Memory

### 3.1 Install SQLite (Built into Python)
No installation needed - SQLite is included with Python!

### 3.2 Create Memory Manager
Create `C:\coco\core\memory_manager.py`:

```python
import sqlite3
import json
from datetime import datetime

class MemoryManager:
    def __init__(self, db_path="memory/conversation.db"):
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
        # This is a simple implementation - could be enhanced with NER
        self.cursor.execute("""
            SELECT content, intent
            FROM conversations
            WHERE session_id = ?
            AND role = 'user'
            ORDER BY timestamp DESC
            LIMIT 10
        """, (self.session_id,))
        
        rows = self.cursor.fetchall()
        
        # Simple keyword extraction (can be improved)
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
        
        count = self.cursor.fetchone()[0]
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
    print("✅ Memory manager working!")
```

### 3.3 Create Memory Folder
```powershell
mkdir C:\coco\memory
```

### 3.4 Test Memory Manager
```powershell
python core\memory_manager.py
```

Expected output:
```
Recent context:
User: Open notepad
coco: [Executed: open_app] Opened notepad
User: Type hello world
coco: [Executed: type_text] Typed text
User: Close it

Last app mentioned: notepad
✅ Memory manager working!
```

---

## STEP 4 — Implement Structured LLM Parsing

### 4.1 Update System Prompt for JSON Output

Create `C:\coco\core\prompts.py`:

```python
AGENT_SYSTEM_PROMPT = """You are coco, a powerful AI agent with system control capabilities.

You can execute actions through skills. When the user asks you to do something, analyze the request and respond with JSON.

Available skills:
- browser: open_website, search_google, close_browser
- system: open_app, close_app, list_apps, minimize_window, maximize_window
- keyboard: type_text, press_key, press_hotkey, click_at, screenshot
- screen: read_screen
- files: create_file, read_file, delete_file, list_files

Response Format (always JSON):
{
  "intent": "skill_name.action_name or null",
  "parameters": {"param": "value"} or {},
  "needs_context": true/false,
  "response": "What to say to user"
}

Examples:

User: "Open notepad"
{
  "intent": "system.open_app",
  "parameters": {"app": "notepad"},
  "needs_context": false,
  "response": "Opening notepad"
}

User: "Search google for AI news"
{
  "intent": "browser.search_google",
  "parameters": {"query": "AI news"},
  "needs_context": false,
  "response": "Searching Google for AI news"
}

User: "Close it" (after opening notepad)
{
  "intent": "system.close_app",
  "parameters": {"app": "notepad"},
  "needs_context": true,
  "response": "Closing notepad"
}

User: "What's the weather like?"
{
  "intent": null,
  "parameters": {},
  "needs_context": false,
  "response": "I don't have weather capabilities yet, but you could ask me to search Google for the weather in your area."
}

CRITICAL: Always respond with valid JSON only. No markdown, no explanation, just JSON."""

def build_prompt_with_context(user_input, conversation_context=""):
    """Build complete prompt with conversation context"""
    if conversation_context:
        return f"""Recent conversation:
{conversation_context}

Current request: {user_input}

Analyze this request with the conversation context in mind. Respond with JSON."""
    else:
        return f"User request: {user_input}\n\nRespond with JSON."
```

---

## STEP 5 — Create Refined Agent (Phase 2.5)

Create `C:\coco\core\coco_refined.py`:

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

# Add coco to path
sys.path.append('C:/coco')

from core.skill_manager import SkillManager
from core.wake_detector import WakeDetector
from core.memory_manager import MemoryManager
from core.prompts import AGENT_SYSTEM_PROMPT, build_prompt_with_context

# Load environment variables
load_dotenv()

# Load models with GPU support
print("[coco] Loading Whisper on GPU...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[coco] Using device: {device}")
stt_model = whisper.load_model("medium", device=device)

print("[coco] Loading Kokoro...")
tts_model = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

print("[coco] Initializing wake detector...")
wake_detector = WakeDetector(clap_threshold=0.3)

print("[coco] Loading skills...")
skills = SkillManager()

print("[coco] Initializing memory...")
memory = MemoryManager()

# Cloud API Configuration
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"
OLLAMA_MODEL = "gpt-oss:120b"

def record_audio(duration=5, sample_rate=16000):
    """Record audio from microphone"""
    print("[coco] Listening...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    wav.write("temp_input.wav", sample_rate, audio)
    return "temp_input.wav"

def transcribe(audio_path):
    """Transcribe audio to text using Whisper"""
    result = stt_model.transcribe(audio_path)
    return result['text'].strip()

def think(user_input, conversation_context=""):
    """Send request to LLM and get structured response"""
    headers = {
        'Authorization': f'Bearer {OLLAMA_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    user_prompt = build_prompt_with_context(user_input, conversation_context)
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_CLOUD_URL, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            content = response.json()['message']['content'].strip()
            
            # Try to parse JSON
            try:
                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "intent": None,
                    "parameters": {},
                    "needs_context": False,
                    "response": content
                }
        else:
            return {
                "intent": None,
                "parameters": {},
                "needs_context": False,
                "response": f"Error: Cloud API returned {response.status_code}"
            }
    except Exception as e:
        return {
            "intent": None,
            "parameters": {},
            "needs_context": False,
            "response": f"Error: {str(e)}"
        }

def speak(text):
    """Convert text to speech and play"""
    print(f"[coco] {text}")
    samples, sample_rate = tts_model.create(text, voice="af_bella", speed=1.0, lang="en-us")
    sd.play(samples, sample_rate)
    sd.wait()

def execute_skill(intent, parameters):
    """Execute skill based on intent"""
    if not intent or intent == "null":
        return None
    
    try:
        # Parse skill.action format
        skill_name, action_name = intent.split(".")
        
        # Map to skill manager
        if skill_name == "browser":
            if action_name == "open_website":
                return skills.browser.open_website(parameters.get('url', ''))
            elif action_name == "search_google":
                return skills.browser.search_google(parameters.get('query', ''))
            elif action_name == "close_browser":
                return skills.browser.close_browser()
        
        elif skill_name == "system":
            if action_name == "open_app":
                return skills.system.open_application(parameters.get('app', ''))
            elif action_name == "close_app":
                return skills.system.close_application(parameters.get('app', ''))
            elif action_name == "list_apps":
                apps = skills.system.list_running_apps()
                return f"Running apps: {', '.join(apps[:10])}"
        
        elif skill_name == "keyboard":
            if action_name == "type_text":
                return skills.keyboard.type_text(parameters.get('text', ''))
            elif action_name == "screenshot":
                return skills.keyboard.take_screenshot()
        
        elif skill_name == "screen":
            if action_name == "read_screen":
                return skills.screen.read_screen()
        
        elif skill_name == "files":
            if action_name == "create_file":
                return skills.files.create_file(
                    parameters.get('filepath', 'new_file.txt'),
                    parameters.get('content', '')
                )
            elif action_name == "list_files":
                files = skills.files.list_files(parameters.get('folder', '.'))
                return f"Files: {', '.join(files[:15])}"
        
        return f"Unknown skill action: {intent}"
    
    except Exception as e:
        return f"Error executing skill: {str(e)}"

# Main Loop
print("\n" + "="*50)
print("  coco Agent v2.5 - Double-Clap Wake Enabled")
print("="*50)
print("\n[coco] Ready! Clap twice to wake me up.")
print("[coco] Say 'exit' or 'shutdown coco' to stop.\n")

try:
    while True:
        # Wait for double-clap wake signal
        if wake_detector.listen_for_wake(duration=0.5):
            print("👏👏 [Wake] Double-clap detected!")
            speak("Yes?")
            
            # Record user command
            audio_path = record_audio(duration=5)
            user_text = transcribe(audio_path)
            
            if not user_text:
                continue
            
            print(f"[You] {user_text}")
            
            # Check for exit commands
            if any(word in user_text.lower() for word in ["exit", "quit", "shutdown coco", "goodbye"]):
                speak("Shutting down. Goodbye!")
                break
            
            # Add to memory
            memory.add_interaction("user", user_text)
            
            # Get conversation context
            context = memory.get_recent_context(limit=5)
            
            # Get LLM response with structured output
            llm_response = think(user_text, context)
            
            # Execute skill if needed
            action_result = None
            if llm_response.get("intent"):
                action_result = execute_skill(
                    llm_response["intent"],
                    llm_response.get("parameters", {})
                )
                
                if action_result:
                    print(f"[Action] {action_result}")
            
            # Speak response
            speak(llm_response["response"])
            
            # Add to memory
            memory.add_interaction(
                "assistant",
                llm_response["response"],
                intent=llm_response.get("intent"),
                action_result=action_result
            )

except KeyboardInterrupt:
    print("\n\n[coco] Interrupted by user")

finally:
    # Cleanup
    print("\n[coco] Cleaning up...")
    skills.browser.close_browser()
    memory.close()
    print("[coco] Session ended")
    print(f"[coco] {memory.get_session_summary()}")
```

---

## STEP 6 — Update Requirements

Update `C:\coco\requirements.txt` - add these new lines:

```
librosa
torch
torchvision
torchaudio
```

Full requirements file should now have:
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
librosa
torch
torchvision
torchaudio
```

---

## STEP 7 — Test Phase 2.5

### 7.1 Run Refined Agent
```powershell
cd C:\coco
.\venv\Scripts\activate
python core\coco_refined.py
```

### 7.2 Test Workflow

**Wake Detection:**
1. Wait for "[coco] Ready! Clap twice to wake me up"
2. Clap twice quickly (0.3s gap)
3. Should hear "Yes?"
4. Speak your command within 5 seconds

**Test Memory:**
1. Clap → "Open notepad"
2. Wait for notepad to open
3. Clap → "Close it" (no need to say "notepad" again!)
4. Should close the previously opened app

**Test GPU Speed:**
1. Clap → Say something
2. Transcription should be ~1-2 seconds (not 5-10 seconds)

**Test Structured Parsing:**
1. Clap → "Could you please open calculator?"
2. Should still work (more robust parsing)

---

## STEP 8 — Create Launch Script

Create `C:\coco\run_coco_v2.5.bat`:

```batch
@echo off
cd C:\coco
call venv\Scripts\activate
echo.
echo ========================================
echo    coco Agent v2.5 - Refined Edition
echo ========================================
echo  Double-Clap Wake + Memory + GPU
echo ========================================
echo.
python core\coco_refined.py
pause
```

Double-click this to launch coco v2.5!

---

## Phase 2.5 Completion Checklist

| Feature | Status |
|---------|--------|
| PyTorch CUDA installed | ✅ |
| Whisper GPU acceleration working | ✅ |
| Double-clap wake detection calibrated | ✅ |
| Wake detector tested and functional | ✅ |
| SQLite memory database created | ✅ |
| Memory manager storing conversations | ✅ |
| Structured JSON parsing from LLM | ✅ |
| Context awareness working ("close it") | ✅ |
| All Phase 2 skills still functional | ✅ |
| Full refined agent operational | ✅ |

---

## Performance Improvements

**Before Phase 2.5:**
- Wake: Always listening = CPU waste
- Transcription: 5-10 seconds (CPU)
- Memory: None
- Parsing: Fragile regex

**After Phase 2.5:**
- Wake: 👏👏 = Instant, low CPU
- Transcription: 1-2 seconds (GPU) = **5-10x faster!**
- Memory: Full context awareness
- Parsing: Robust JSON structure

---

## Advanced Configuration

### Adjust Clap Sensitivity

In `wake_detector.py`, modify:
```python
detector = WakeDetector(
    clap_threshold=0.3,    # Lower = more sensitive, Higher = less sensitive
    clap_gap_min=0.1,      # Minimum time between claps
    clap_gap_max=0.6       # Maximum time between claps
)
```

### Adjust Memory Depth

In `coco_refined.py`, modify:
```python
context = memory.get_recent_context(limit=5)  # Remember last 5 interactions
```

### Change Recording Duration

In `coco_refined.py`:
```python
audio_path = record_audio(duration=5)  # Listen for 5 seconds after wake
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| GPU not detected | Reinstall PyTorch with CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu118` |
| Double-clap not triggering | Run calibration: `python core\wake_detector.py` and type `y` |
| Clap too sensitive (triggers randomly) | Increase `clap_threshold` from 0.3 to 0.4 or 0.5 |
| Memory not saving | Check `C:\coco\memory\` folder exists |
| JSON parsing errors | LLM sometimes adds markdown - code strips it automatically |
| "Close it" not working | Make sure previous command was logged in memory |

---

## What's Next: Phase 3

Phase 3 will add:
- **Multi-step task execution** - "Open notepad, type hello, then save it"
- **Scheduled automation** - "Check my email every hour"
- **Custom workflow builder** - Create reusable automation sequences
- **Service integrations** - Email, calendar, Spotify, etc.
- **Learning from patterns** - coco learns your common tasks

---

🎉 **Congratulations!**

coco is now a refined, fast, context-aware agent with:
- Natural wake detection (double-clap)
- GPU-accelerated speech recognition
- Full conversation memory
- Robust intent parsing
- All system control capabilities from Phase 2

You can now have natural conversations like:
- 👏👏 "Open Chrome and search for Python tutorials"
- 👏👏 "Take a screenshot"
- 👏👏 "Close it" (remembers what to close!)

Your AI agent is getting seriously powerful! 🚀
