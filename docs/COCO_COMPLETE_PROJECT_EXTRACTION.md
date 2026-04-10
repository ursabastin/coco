# coco — Complete Project Extraction & Documentation
### Full Structure, Features, Architecture & Implementation Details

---

## Project Overview

**Project Name:** coco  
**Type:** Local AI Voice Assistant with System Automation  
**Platform:** Windows 11  
**Language:** Python 3.11  
**Primary Framework:** Playwright, Whisper, Ollama Cloud, Kokoro TTS  

**Core Concept:**  
A fully functional AI assistant that runs locally on your laptop with cloud-based intelligence, featuring voice interaction, system control, browser automation, and intelligent task execution.

---

## Complete File Structure

```
C:\coco\
│
├── .env                          # API keys and secrets
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Python dependencies
├── config.yaml                   # Configuration settings
├── main.py                       # Entry point (placeholder)
│
├── core/                         # Core agent logic
│   ├── coco_core.py             # Phase 1: Basic STT→LLM→TTS loop
│   ├── coco_agent.py            # Phase 2: With skills integration
│   ├── coco_refined.py          # Phase 2.5: Wake detection + memory + GPU
│   ├── coco_advanced.py         # Phase 3: Multi-step + scheduling + workflows
│   ├── skill_manager.py         # Orchestrates all skills
│   ├── task_executor.py         # Multi-step task execution
│   ├── scheduler.py             # Background task scheduling
│   ├── workflow_manager.py      # Save/load automation workflows
│   ├── wake_detector.py         # Double-clap wake detection
│   ├── memory_manager.py        # Conversation memory (SQLite)
│   ├── pattern_learner.py       # Usage pattern analysis
│   ├── network_monitor.py       # Network speed detection
│   ├── voice_confirmation.py    # Voice yes/no prompts
│   ├── progress_notifier.py     # Long operation updates
│   └── prompts.py               # LLM system prompts
│
├── skills/                       # Modular capabilities
│   ├── __init__.py
│   ├── browser_skill.py         # Web automation (Playwright)
│   ├── system_skill.py          # Windows control
│   ├── keyboard_skill.py        # Keyboard/mouse automation
│   ├── screen_skill.py          # OCR screen reading
│   ├── file_skill.py            # File operations
│   ├── test_playwright.py       # Browser testing
│   ├── test_system.py           # System control testing
│   ├── test_ocr.py              # OCR testing
│   └── test_browser_profile.py  # Profile detection
│
├── integrations/                 # External service connectors
│   ├── __init__.py
│   ├── gmail_integration.py     # Gmail API (optional)
│   ├── calendar_integration.py  # Google Calendar (optional)
│   ├── spotify_integration.py   # Spotify control (optional)
│   └── weather_integration.py   # Weather data (wttr.in)
│
├── stt/                          # Speech-to-Text
│   └── test_stt.py              # Whisper testing
│
├── tts/                          # Text-to-Speech
│   ├── kokoro-v0_19.onnx        # Kokoro model file
│   ├── voices.bin               # Voice data
│   └── test_tts.py              # Kokoro testing
│
├── brain/                        # LLM interface
│   ├── test_cloud.py            # Ollama Cloud API testing
│   └── test_gpu.py              # GPU detection testing
│
├── memory/                       # Persistent data
│   ├── conversation.db          # Chat history (SQLite)
│   └── patterns.db              # Learned usage patterns
│
├── workflows/                    # Saved automation sequences
│   ├── morning_routine.json     # Example workflow
│   └── screenshot_and_save.json # Example workflow
│
├── scheduler/                    # Scheduled tasks
│   └── tasks.db                 # Task definitions (SQLite)
│
├── venv/                         # Python virtual environment
│   └── [Python packages]
│
├── run_coco_v2.5.bat            # Launch Phase 2.5
├── run_agent.bat                # Launch Phase 2
├── test_browser_now.py          # Browser quick test
├── test_network_handling.py     # Network handling test
├── test_basic_loop.py           # Basic audio loop test
└── test_slow_network.py         # Slow network simulation
```

---

## Phase-by-Phase Feature Breakdown

### **Phase 1: Foundation Setup**
**Status:** ✅ Complete  
**File:** `core/coco_core.py`

**Features:**
- Cloud-based LLM (Ollama Cloud API with gpt-oss:120b model)
- Local Speech-to-Text (Whisper Medium on CPU)
- Local Text-to-Speech (Kokoro with af_bella voice)
- Basic conversation loop
- API key management via .env file

**How it Works:**
1. User speaks
2. Whisper transcribes to text
3. Text sent to Ollama Cloud API
4. LLM generates response
5. Kokoro converts response to speech
6. User hears response
7. Loop repeats

**Dependencies:**
- `openai-whisper` - Speech recognition
- `kokoro-onnx` - Text-to-speech
- `requests` - API calls
- `python-dotenv` - Environment variables
- `sounddevice`, `scipy`, `numpy` - Audio handling

---

### **Phase 2: System Automation & Skills**
**Status:** ✅ Complete  
**File:** `core/coco_agent.py`

**Features:**
- **Browser Automation** (Playwright)
  - Open websites
  - Search Google
  - Click elements
  - Fill forms
  - Take screenshots
  
- **System Control**
  - Open/close applications
  - List running processes
  - Minimize/maximize windows
  - System shutdown/restart
  
- **Keyboard & Mouse**
  - Type text anywhere
  - Press hotkeys (Ctrl+C, etc.)
  - Click at coordinates
  - Move mouse programmatically
  
- **Screen Reading** (EasyOCR)
  - Read all text from screen
  - Read specific regions
  - Text extraction from any window
  
- **File Operations**
  - Create, read, delete files
  - Copy, move files
  - Create folders
  - List directories

**How it Works:**
1. User command received
2. `SkillManager` routes to appropriate skill
3. Skill executes action (browser, system, keyboard, etc.)
4. Result returned to user
5. Action logged

**Dependencies:**
- `playwright` - Browser automation
- `pyautogui` - Keyboard/mouse control
- `psutil` - Process management
- `pygetwindow` - Window control
- `easyocr` - OCR text reading
- `opencv-python` - Image processing

---

### **Phase 2.5: Essential Refinements**
**Status:** ✅ Complete  
**File:** `core/coco_refined.py`

**Features:**
- **Double-Clap Wake Detection**
  - Audio-based clap detection
  - No wake word needed (language-agnostic)
  - Calibration system for environment
  - Adjustable sensitivity
  
- **Conversation Memory** (SQLite)
  - Stores all interactions
  - Session tracking
  - Context-aware responses
  - Can reference previous commands ("close it")
  
- **GPU Acceleration**
  - Whisper runs on RTX 3050
  - 5-10x faster transcription (1-2s vs 5-10s)
  - CUDA support via PyTorch
  
- **Structured LLM Parsing**
  - JSON-based responses
  - Robust intent extraction
  - Better error handling
  - Context injection

**How it Works:**
1. **Wake Loop:** Continuously monitors audio for double-clap
2. **Clap Detection:** RMS amplitude analysis finds sudden loud sounds
3. **Gap Analysis:** Checks if two claps are 0.1-0.6s apart
4. **Activation:** On detection, speaks "Yes?" and listens
5. **Command Processing:** Same as Phase 2 but with memory context
6. **Memory Storage:** Saves user input, intent, and result to SQLite
7. **GPU Transcription:** Whisper on CUDA for fast processing

**Dependencies:**
- `librosa` - Audio analysis
- `torch` (with CUDA) - GPU acceleration
- `sqlite3` - Database (built-in)

---

### **Phase 3: Advanced Intelligence**
**Status:** ✅ Complete  
**File:** `core/coco_advanced.py`

**Features:**
- **Multi-Step Task Execution**
  - Chain multiple actions: "Open notepad AND type hello AND save"
  - Sequential execution with delays
  - Error recovery between steps
  - Step-by-step logging
  
- **Task Scheduling** (APScheduler)
  - Interval tasks: "Check weather every hour"
  - Time-based: "Remind me at 3pm"
  - Daily schedules: "Run morning routine at 8am"
  - Persistent across restarts
  
- **Workflow System**
  - Save complex automation sequences
  - Pre-built workflows (morning_routine, etc.)
  - Import/export workflows (JSON)
  - Reusable task templates
  
- **Service Integrations**
  - Weather (wttr.in - no API key)
  - Gmail (Google API - optional)
  - Calendar (Google API - optional)
  - Spotify (Spotipy - optional)
  
- **Pattern Learning**
  - Tracks command frequency
  - Time-of-day patterns
  - Usage statistics
  - Smart suggestions

**How it Works:**

**Multi-Step:**
1. LLM returns `steps` array in JSON
2. `TaskExecutor` iterates through steps
3. Each step executed via `SkillManager`
4. Optional delays between steps
5. Results aggregated and reported

**Scheduling:**
1. User requests scheduled task
2. `TaskScheduler` creates APScheduler job
3. Task saved to `scheduler/tasks.db`
4. Job runs in background thread
5. Executes defined skill actions
6. Updates last run timestamp

**Workflows:**
1. User creates or loads workflow
2. Workflow stored as JSON in `workflows/`
3. Contains array of steps with intents/parameters
4. Can be executed by name
5. Treated as multi-step task

**Pattern Learning:**
1. Every command logged to `patterns.db`
2. Tracks: command, intent, frequency, time, day
3. Analyzes patterns for suggestions
4. Can suggest based on time of day

**Dependencies:**
- `apscheduler` - Task scheduling
- `google-api-python-client` - Google services
- `spotipy` - Spotify control
- `python-dateutil` - Date handling

---

### **Phase 3.5: Browser Refinements**
**Status:** ✅ Complete  
**File:** `skills/browser_skill.py` (updated)

**Features:**
- **Default Browser Detection**
  - Reads Windows registry
  - Detects Chrome, Edge, Firefox
  - Uses installed browser (not Chromium)
  
- **Real User Profile**
  - Loads saved passwords
  - Preserves browsing history
  - Maintains logged-in sessions
  - Uses bookmarks and extensions
  
- **Smart URL Parsing**
  - "youtube" → youtube.com
  - "google" → google.com
  - Common site mappings (20+ sites)
  - Auto-adds https://
  
- **Actual Execution**
  - Fixed skill routing
  - Browser actions now execute
  - Proper error handling

**How it Works:**
1. **Browser Detection:** Reads registry key for default browser
2. **Profile Path:** Constructs path to User Data folder
3. **Launch:** Uses `launch_persistent_context` with profile
4. **URL Normalization:** Maps common names to full URLs
5. **Navigation:** Opens site with proper wait conditions

**Path Examples:**
- Chrome: `C:\Users\{user}\AppData\Local\Google\Chrome\User Data`
- Edge: `C:\Users\{user}\AppData\Local\Microsoft\Edge\User Data`

---

### **Phase 3.6: Network Handling**
**Status:** ✅ Complete  
**Files:** `core/network_monitor.py`, `core/voice_confirmation.py`

**Features:**
- **Network Speed Detection**
  - Background monitoring (every 60s)
  - Download speed test (KB/s)
  - Slow threshold: <50 KB/s
  - Automatic status updates
  
- **Adaptive Timeouts**
  - Normal network: 30s timeout
  - Slow network: 90s timeout (3x)
  - Dynamic adjustment based on speed
  
- **Voice Confirmation**
  - Asks: "Network is slow, should I wait?"
  - Listens for voice response
  - Parses yes/no
  - Acts on user decision
  
- **Retry Logic**
  - Up to 3 attempts per page
  - Asks before each retry
  - User can cancel anytime
  
- **Progress Updates**
  - Periodic notifications (every 15s)
  - "Still working on it" messages
  - User knows system is active

**How it Works:**

**Network Monitoring:**
1. Background thread runs every 60s
2. Downloads small file (Google homepage)
3. Measures time and calculates KB/s
4. Sets `is_slow` flag if <50 KB/s
5. Stores result for use by skills

**Adaptive Timeout:**
1. Browser skill checks network status
2. If slow: timeout = base * 3
3. If normal: timeout = base
4. Applied to page.goto() calls

**Voice Confirmation:**
1. Network detected as slow
2. TTS: "Network is slow, should I wait?"
3. STT: Records 10s of audio
4. Transcribes response
5. Parses for yes/no keywords
6. Returns boolean decision

**Retry Flow:**
1. Page load attempted with timeout
2. If timeout: Ask "Try again?"
3. If yes: Retry with same timeout
4. If no: Return "Cancelled"
5. Max 3 attempts total

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                    (Voice Commands)                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    WAKE DETECTOR                             │
│              (Double-Clap Detection)                         │
│   - Audio monitoring - RMS analysis - Gap detection         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼ (on wake)
┌─────────────────────────────────────────────────────────────┐
│                  SPEECH-TO-TEXT                              │
│                 (Whisper on GPU)                             │
│   - Record 5s audio - Transcribe - Return text              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  MEMORY MANAGER                              │
│            (Conversation Context)                            │
│   - Store user input - Retrieve recent history              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM (Cloud)                               │
│              (Ollama gpt-oss:120b)                           │
│   - Input: User text + context                              │
│   - Output: JSON {type, intent, parameters, response}       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  TASK EXECUTOR                               │
│              (Action Router)                                 │
│   - Parse JSON response - Route to skill - Handle errors    │
└─────────────────┬───────────────────────────────────────────┘
                  │
      ┌───────────┴───────────┬───────────────┬───────────────┐
      ▼                       ▼               ▼               ▼
┌──────────┐          ┌──────────┐     ┌──────────┐   ┌──────────┐
│ BROWSER  │          │  SYSTEM  │     │ KEYBOARD │   │  FILES   │
│  SKILL   │          │  SKILL   │     │  SKILL   │   │  SKILL   │
├──────────┤          ├──────────┤     ├──────────┤   ├──────────┤
│ Open URL │          │ Open app │     │ Type     │   │ Create   │
│ Search   │          │ Close    │     │ Click    │   │ Read     │
│ Click    │          │ List     │     │ Hotkey   │   │ Delete   │
└──────────┘          └──────────┘     └──────────┘   └──────────┘
      │                       │               │               │
      └───────────┬───────────┴───────────────┴───────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              TEXT-TO-SPEECH (Kokoro)                         │
│   - Generate audio - Play through speakers                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                   (Hears Response)                           │
└─────────────────────────────────────────────────────────────┘

PARALLEL SYSTEMS:

┌─────────────────────────────────────────────────────────────┐
│              NETWORK MONITOR (Background)                    │
│   - Test speed every 60s - Set slow flag                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              TASK SCHEDULER (Background)                     │
│   - Run scheduled tasks - Execute workflows                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              PATTERN LEARNER (Background)                    │
│   - Log all commands - Build usage patterns                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow Examples

### Example 1: Simple Command
```
User: 👏👏 "Open YouTube"

1. WakeDetector detects double-clap → Speak "Yes?"
2. Record 5 seconds of audio
3. Whisper transcribes: "Open YouTube"
4. MemoryManager saves: user said "Open YouTube"
5. Get recent context from database
6. Send to LLM:
   {
     "context": "...",
     "input": "Open YouTube"
   }
7. LLM returns:
   {
     "type": "single",
     "intent": "browser.open_website",
     "parameters": {"url": "youtube"},
     "response": "Opening YouTube"
   }
8. TaskExecutor routes to BrowserSkill
9. BrowserSkill.normalize_url("youtube") → "https://youtube.com"
10. Check network speed → normal
11. Open browser with 30s timeout
12. Page loads successfully
13. MemoryManager saves result
14. PatternLearner logs: "open youtube" → browser.open_website
15. Kokoro speaks: "Opening YouTube"
16. Return to wake detection loop
```

### Example 2: Multi-Step Command
```
User: 👏👏 "Open notepad and type hello world"

1-6. [Same as Example 1]
7. LLM returns:
   {
     "type": "multi_step",
     "steps": [
       {
         "intent": "system.open_app",
         "parameters": {"app": "notepad"},
         "description": "Open notepad",
         "delay": 1
       },
       {
         "intent": "keyboard.type_text",
         "parameters": {"text": "hello world"},
         "description": "Type text",
         "delay": 0
       }
     ],
     "response": "Opening notepad and typing the text"
   }
8. TaskExecutor.execute_multi_step_task(steps)
9. Step 1: SystemSkill.open_application("notepad")
   → Notepad opens
10. Wait 1 second (delay)
11. Step 2: KeyboardSkill.type_text("hello world")
    → Text appears in notepad
12. Summary: "Completed 2/2 steps successfully"
13. Speak summary
14. Return to wake detection
```

### Example 3: Slow Network with Confirmation
```
User: 👏👏 "Open GitHub"

1-6. [Same as Example 1]
7. LLM returns single action: browser.open_website
8. BrowserSkill checks NetworkMonitor
9. NetworkMonitor.is_slow = True (speed: 35 KB/s)
10. Timeout extended: 30s → 90s
11. VoiceConfirmation.ask_yes_no("Network is slow...")
12. Kokoro speaks: "Network is slow. Should I continue waiting?"
13. Record 10s for response
14. User says: "Yes"
15. Whisper transcribes: "yes"
16. Parse: Contains "yes" → return True
17. Continue with 90s timeout
18. page.goto("https://github.com", timeout=90000)
19. Page loads after 65 seconds
20. Success: "Opened GitHub"
21. Return to wake detection
```

---

## Database Schemas

### conversation.db (Memory)
```sql
-- Conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    timestamp TEXT,
    role TEXT,               -- 'user' or 'assistant'
    content TEXT,            -- What was said/responded
    intent TEXT,             -- Skill action executed
    action_result TEXT       -- Result of action
);

-- Sessions table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    start_time TEXT,
    end_time TEXT,
    total_interactions INTEGER
);
```

### patterns.db (Pattern Learning)
```sql
CREATE TABLE command_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT,            -- User's command
    intent TEXT,             -- Mapped intent
    frequency INTEGER,       -- Times used
    last_used TEXT,          -- Last timestamp
    time_of_day TEXT,        -- morning/afternoon/evening/night
    day_of_week TEXT         -- Monday, Tuesday, etc.
);
```

### tasks.db (Scheduler)
```sql
CREATE TABLE scheduled_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,               -- Task identifier
    schedule_type TEXT,      -- 'interval' or 'daily'
    schedule_config TEXT,    -- JSON config
    task_config TEXT,        -- JSON task definition
    enabled INTEGER,         -- 1 or 0
    last_run TEXT,           -- Last execution time
    next_run TEXT            -- Next scheduled time
);
```

---

## Configuration Files

### .env
```env
OLLAMA_API_KEY=ollama_xxxxxxxxxxxxxxxxxxxx
```

### requirements.txt
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
apscheduler
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
spotipy
python-dateutil
```

---

## Key Technologies & Why They Were Chosen

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Whisper (OpenAI)** | Speech-to-Text | Best open-source STT, GPU support, offline |
| **Kokoro** | Text-to-Speech | Fast, natural voices, offline, free |
| **Ollama Cloud** | LLM Intelligence | Powerful model (120B), no local GPU load, free tier |
| **Playwright** | Browser Automation | Modern, supports all browsers, user profile loading |
| **PyAutoGUI** | System Control | Cross-platform, keyboard/mouse automation |
| **EasyOCR** | Screen Reading | Accurate text recognition, offline |
| **APScheduler** | Task Scheduling | Background jobs, cron-like, Python-native |
| **SQLite** | Data Storage | Serverless, fast, built-in, perfect for local data |
| **PyTorch (CUDA)** | GPU Acceleration | Industry standard, Whisper support, RTX compatible |
| **SoundDevice** | Audio I/O | Low-latency, cross-platform, real-time audio |

---

## Performance Specifications

### Current System Performance

**Hardware:**
- CPU: Intel i5-12450H (8 cores, 12 threads)
- RAM: 16GB DDR4 3200MHz
- GPU: NVIDIA RTX 3050 (4GB VRAM)
- Storage: 511GB SSD (144GB free)

**Speed Benchmarks:**
- Wake detection: <100ms latency
- STT (Whisper GPU): 1-2 seconds for 5s audio
- STT (Whisper CPU): 5-10 seconds for 5s audio
- LLM response: 2-5 seconds (network dependent)
- TTS generation: <500ms
- TTS playback: Real-time
- Browser launch: 2-3 seconds
- Skill execution: <1 second (average)

**Resource Usage:**
- Idle: ~500MB RAM, <5% CPU
- Active (listening): ~800MB RAM, 10-15% CPU
- Processing: ~2GB RAM, 40-60% CPU, 30-50% GPU
- With browser: +200MB RAM per page

---

## Workflow Examples

### Workflow: morning_routine.json
```json
{
  "name": "morning_routine",
  "description": "Open essential apps for the day",
  "steps": [
    {
      "intent": "browser.open_website",
      "parameters": {"url": "gmail.com"},
      "description": "Open email",
      "delay": 0
    },
    {
      "intent": "browser.open_website",
      "parameters": {"url": "calendar.google.com"},
      "description": "Open calendar",
      "delay": 2
    },
    {
      "intent": "system.open_app",
      "parameters": {"app": "notepad"},
      "description": "Open notepad for notes",
      "delay": 1
    }
  ],
  "created_at": "2026-04-10T10:30:00",
  "version": "1.0"
}
```

---

## Error Handling Strategy

### Levels of Error Handling

**Level 1: Graceful Degradation**
- Network timeout → Retry with user confirmation
- Skill not found → Inform user, don't crash
- LLM parsing error → Fallback to text response

**Level 2: User Notification**
- Slow network → Voice warning
- Missing file → Speak error message
- Permission denied → Explain what's needed

**Level 3: Automatic Recovery**
- Browser crash → Relaunch browser
- API timeout → Retry with backoff
- Audio device error → Switch to fallback device

**Level 4: Logging**
- All errors logged to console
- Failed tasks saved to database
- Pattern of failures tracked

---

## Security & Privacy

### Data Privacy
- ✅ All voice processing local (Whisper)
- ✅ All TTS local (Kokoro)
- ⚠️ Commands sent to Ollama Cloud (but not stored)
- ✅ Conversation history local SQLite
- ✅ No telemetry or tracking
- ✅ API keys in .env (not in code)

### Browser Security
- Uses real user profile (passwords accessible)
- No sandboxing (full system control)
- Playwright automation detectable by sites
- Consider security implications before use

---

## Known Limitations

1. **Language:** English only (models trained on English)
2. **Platform:** Windows only (some features Windows-specific)
3. **Network:** Requires internet for LLM (Ollama Cloud)
4. **Wake Detection:** Ambient noise can cause false positives
5. **OCR:** Struggles with handwriting or artistic fonts
6. **Browser:** Some sites detect automation and block
7. **Voice:** Struggles with heavy accents or background noise

---

## Future Enhancement Ideas

**Phase 4 (Potential):**
- Multi-language support
- Custom wake words (not just claps)
- Visual dashboard (web UI)
- Mobile companion app
- Cloud sync for workflows
- More service integrations
- Voice customization
- Emotion detection in speech
- Proactive suggestions
- Learning from corrections

---

## Troubleshooting Quick Reference

| Problem | File to Check | Solution |
|---------|---------------|----------|
| Can't hear coco | `test_audio_devices.py` | Check speaker settings |
| coco can't hear me | `test_audio_devices.py` | Check microphone settings |
| Double-clap not working | `wake_detector.py` | Run calibration |
| Browser not opening | `test_browser_now.py` | Check Playwright install |
| Wrong browser opens | `browser_skill.py` | Check registry detection |
| Not logged in browser | `test_browser_profile.py` | Check profile path |
| Network timeouts | `network_monitor.py` | Check speed, adjust threshold |
| GPU not used | `test_gpu.py` | Reinstall PyTorch with CUDA |
| Slow transcription | `test_gpu.py` | Enable GPU acceleration |
| API errors | `.env` | Check API key |
| Memory not working | `memory/conversation.db` | Check database exists |
| Scheduled tasks not running | `scheduler/tasks.db` | Check scheduler started |

---

## Complete Command Reference

### Voice Commands Supported

**Browser:**
- "Open [website]" → Opens site
- "Search Google for [query]" → Searches
- "Close browser" → Closes browser

**System:**
- "Open [app]" → Opens application
- "Close [app]" → Closes application
- "What apps are running" → Lists processes
- "Take a screenshot" → Captures screen

**Files:**
- "Create file [name]" → Creates file
- "Read file [name]" → Reads content
- "List files" → Shows directory

**Screen:**
- "Read the screen" → OCR current display
- "What's on screen" → Same as above

**Keyboard:**
- "Type [text]" → Types text
- "Press [key]" → Presses key

**Multi-Step:**
- "Open [app] and type [text]" → Chains actions
- "Search [query] and take screenshot" → Sequential

**Scheduling:**
- "Check [thing] every [time]" → Schedules task
- "Remind me at [time]" → Time-based reminder

**Workflows:**
- "Run [workflow name]" → Executes saved workflow
- "Run morning routine" → Executes default workflow

**Integrations:**
- "What's the weather" → Gets weather
- "What's the weather in [city]" → City weather

**Conversation:**
- "Exit" / "Quit" / "Shutdown coco" → Stops agent

---

## Development Status

### Completed ✅
- Phase 1: Foundation
- Phase 2: Skills Framework
- Phase 2.5: Refinements
- Phase 3: Advanced Intelligence
- Phase 3.5: Browser Improvements
- Phase 3.6: Network Handling

### In Progress 🔄
- Audio device configuration
- User testing and feedback

### Planned 📋
- Phase 4: Advanced features
- Mobile companion
- Visual dashboard
- More integrations

---

## Project Statistics

- **Total Files:** ~50+
- **Lines of Code:** ~5,000+
- **Python Modules:** 15+
- **Skills:** 5 (Browser, System, Keyboard, Screen, Files)
- **Integrations:** 4 (Weather, Gmail, Calendar, Spotify)
- **Workflows:** 2+ (customizable)
- **Dependencies:** 25+
- **Database Tables:** 5
- **Supported Commands:** 50+

---

## Quick Start Guide

```powershell
# 1. Install Python 3.11
# 2. Create project
cd C:\
mkdir coco
cd coco

# 3. Create venv
python -m venv venv
.\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
playwright install

# 5. Set up API key
# Create .env file with OLLAMA_API_KEY

# 6. Download models
python -c "import whisper; whisper.load_model('medium')"
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='hexgrad/Kokoro-82M', filename='kokoro-v0_19.onnx', local_dir='tts'); hf_hub_download(repo_id='hexgrad/Kokoro-82M', filename='voices.bin', local_dir='tts')"

# 7. Test components
python core\test_audio_devices.py
python core\wake_detector.py
python test_browser_now.py

# 8. Run coco
python core\coco_advanced.py

# 9. Clap twice to wake
# 10. Speak command
# 11. Enjoy!
```

---

## Maintainer Notes

**Created:** April 2026  
**Version:** 3.6  
**Python:** 3.11  
**Platform:** Windows 11  
**Status:** Production Ready  

**Last Updated:** Phase 3.6 (Network Handling)  
**Next Update:** Phase 4 (TBD)

---

🎉 **coco: A fully autonomous local AI assistant with cloud intelligence!**
