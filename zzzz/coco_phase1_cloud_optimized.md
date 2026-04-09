# coco — Phase 1: Foundation Setup (Optimized - Cloud Edition)
### Google Antigravity Build Instructions

---

## Prerequisites Before Starting

Make sure you have the following ready:
- Windows 11 (you have it ✅)
- At least 10GB free on C: drive (reduced from 20GB - no local models!)
- Internet connection (required for cloud API)
- A Google account (for Antigravity sign-in)
- An Ollama account (free - for cloud API access)

---

## STEP 1 — Install Google Antigravity

### 1.1 Download
Go to: `https://antigravity.google`
Click **Download for Windows** → download the `.exe` installer.

### 1.2 Install
Run the installer. It installs like VS Code — accept defaults.
After install, launch **Google Antigravity**.

### 1.3 Sign In
Sign in with your Google account when prompted.

### 1.4 Configure Agent Mode
On the setup screen, select:
- **Mode:** Agent-assisted (recommended)
- **Terminal Policy:** Auto
- Click **Finish**

---

## STEP 2 — Create coco Project in Antigravity

### 2.1 Create Project Folder
Open **PowerShell** and run:

```powershell
mkdir C:\coco
cd C:\coco
mkdir stt, brain, tts, core, skills, memory
New-Item main.py -ItemType File
New-Item config.yaml -ItemType File
New-Item requirements.txt -ItemType File
New-Item .env -ItemType File
```

### 2.2 Open in Antigravity
In Antigravity → **File → Open Folder** → select `C:\coco`

### 2.3 Set Up Python Environment
Open the **Antigravity terminal** (Ctrl + `) and run:

```powershell
python --version
```

If Python is not installed:
- Go to `https://www.python.org/downloads/`
- Download Python 3.11 (recommended, not 3.12)
- During install → check **"Add Python to PATH"**

Then create a virtual environment:

```powershell
cd C:\coco
python -m venv venv
.\venv\Scripts\activate
```

You should see `(venv)` at the start of the terminal line.

---

## STEP 3 — Set Up Ollama Cloud API (No Downloads Required!)

### 3.1 Create Ollama Account
Go to: `https://ollama.com`
Click **Sign Up** and create a free account.

### 3.2 Generate API Key
1. Once signed in, go to: `https://ollama.com/settings/keys`
2. Click **Create new API key**
3. Copy the API key (starts with `ollama_...`)

### 3.3 Store API Key Securely
Open `C:\coco\.env` in Antigravity and add:

```
OLLAMA_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual API key.

### 3.4 Install Python dotenv
In the **Antigravity terminal** (with venv active):

```powershell
pip install python-dotenv
pip install requests
```

### 3.5 Test Cloud API Connection
Create `C:\coco\brain\test_cloud.py`:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"

headers = {
    'Authorization': f'Bearer {OLLAMA_API_KEY}',
    'Content-Type': 'application/json'
}

payload = {
    "model": "gpt-oss:120b",
    "messages": [
        {
            "role": "user",
            "content": "Say hello as coco assistant in one sentence"
        }
    ],
    "stream": False
}

response = requests.post(OLLAMA_CLOUD_URL, json=payload, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Cloud API Working!")
    print(f"Response: {result['message']['content']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
```

Run it:

```powershell
python brain\test_cloud.py
```

Expected: You should see "✅ Cloud API Working!" and a response. This confirms your API key works.

---

## STEP 4 — Install Whisper (Local STT)

### 4.1 Install Dependencies
In the **Antigravity terminal** (with venv active):

```powershell
pip install openai-whisper
pip install sounddevice
pip install scipy
pip install numpy
```

### 4.2 Install FFmpeg (Required by Whisper)

- Go to: `https://ffmpeg.org/download.html`
- Click **Windows builds** → download the zip
- Extract to `C:\ffmpeg`
- Add to PATH:

```powershell
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "Machine")
```

Close and reopen terminal, then verify:

```powershell
ffmpeg -version
```

### 4.3 Download Whisper Medium Model
In Antigravity terminal:

```powershell
python -c "import whisper; whisper.load_model('medium')"
```

This downloads ~1.5GB. This runs on **CPU** (no GPU needed).

### 4.4 Test Whisper
Create `C:\coco\stt\test_stt.py`:

```python
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

print("Recording for 5 seconds... Speak now!")
sample_rate = 16000
duration = 5
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
sd.wait()

wav.write("test_audio.wav", sample_rate, audio)
print("Recording done. Transcribing...")

model = whisper.load_model("medium")
result = model.transcribe("test_audio.wav")
print(f"You said: {result['text']}")
```

Run it:

```powershell
python stt\test_stt.py
```

Speak something when prompted. If your words appear → ✅ Whisper is working.

---

## STEP 5 — Install Kokoro (Local TTS)

### 5.1 Install Kokoro

```powershell
pip install kokoro-onnx
pip install soundfile
pip install pyaudio
```

If `pyaudio` fails, install it this way:

```powershell
pip install pipwin
pipwin install pyaudio
```

### 5.2 Download Kokoro Model Files
```powershell
pip install huggingface_hub
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='hexgrad/Kokoro-82M', filename='kokoro-v0_19.onnx', local_dir='C:/coco/tts'); hf_hub_download(repo_id='hexgrad/Kokoro-82M', filename='voices.bin', local_dir='C:/coco/tts')"
```

This downloads ~350MB total.

### 5.3 Test Kokoro
Create `C:\coco\tts\test_tts.py`:

```python
from kokoro_onnx import Kokoro
import soundfile as sf
import sounddevice as sd

kokoro = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

text = "Hello. I am coco. Your fully cloud-powered AI assistant. I am ready."
samples, sample_rate = kokoro.create(text, voice="af_bella", speed=1.0, lang="en-us")

print("Playing response...")
sd.play(samples, sample_rate)
sd.wait()
print("Done.")
```

Run it:

```powershell
python tts\test_tts.py
```

You should hear coco speak. If audio plays → ✅ Kokoro is working.

---

## STEP 6 — Connect All Three Together (Cloud Edition)

### 6.1 Create Core Loop with Cloud API
Create `C:\coco\core\coco_core.py`:

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

# Load environment variables
load_dotenv()

# Load models
print("[coco] Loading Whisper...")
stt_model = whisper.load_model("medium")

print("[coco] Loading Kokoro...")
tts_model = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

# Cloud API Configuration
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"
OLLAMA_MODEL = "gpt-oss:120b"

SYSTEM_PROMPT = """You are coco, a cloud-powered AI assistant with local voice capabilities.
You are helpful, concise, and smart. Keep responses short and clear.
Never mention being an AI unless asked. You run on Ollama Cloud for intelligence."""

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

# Main Loop
print("[coco] Ready. Starting interaction loop...")
speak("coco is ready. How can I help you?")

while True:
    audio_path = record_audio(duration=5)
    user_text = transcribe(audio_path)

    if not user_text:
        continue

    print(f"[You] {user_text}")

    if any(word in user_text.lower() for word in ["exit", "quit", "shutdown", "stop"]):
        speak("Shutting down coco. Goodbye.")
        break

    response = think(user_text)
    speak(response)
```

### 6.2 Save Requirements
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
```

---

## STEP 7 — First Full Test

### 7.1 Activate Venv and Run coco
In Antigravity terminal:

```powershell
cd C:\coco
.\venv\Scripts\activate
python core\coco_core.py
```

### 7.2 Expected Startup Output

```
[coco] Loading Whisper...
[coco] Loading Kokoro...
[coco] Ready. Starting interaction loop...
[coco] coco is ready. How can I help you?
[coco] Listening...
```

Speak something. coco should transcribe → send to cloud → respond with voice.

---

## Phase 1 Completion Checklist

| Task | Status |
|------|--------|
| Antigravity installed & project opened | ✅ |
| Python venv created and active | ✅ |
| Ollama Cloud account created | ✅ |
| API key generated and stored in .env | ✅ |
| Cloud API responding to test prompts | ✅ |
| Whisper installed + FFmpeg installed | ✅ |
| Whisper transcribing voice correctly | ✅ |
| Kokoro installed + model files downloaded | ✅ |
| Kokoro speaking audio correctly | ✅ |
| Full core loop running end-to-end | ✅ |

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `401 Unauthorized` on API call | Check your API key in .env file |
| `OLLAMA_API_KEY not found` | Make sure .env file exists and is in C:\coco |
| `ffmpeg not found` | Re-add to PATH and restart terminal |
| `No module named 'whisper'` | Make sure venv is active: `.\venv\Scripts\activate` |
| `No module named 'dotenv'` | Run `pip install python-dotenv` |
| `pyaudio install failed` | Use `pipwin install pyaudio` instead |
| Whisper very slow | Normal on first run — model is loading into memory |
| `Connection timeout` | Check internet connection - cloud API needs internet |

---

## Advantages of Cloud Edition

✅ **No GPU Required** - Runs on any laptop  
✅ **No Large Downloads** - Only ~2GB instead of ~4GB+  
✅ **More Powerful Model** - gpt-oss:120b is much smarter than phi3:mini  
✅ **Faster Startup** - No waiting for local model to load  
✅ **Auto Updates** - Model improvements happen on Ollama's side  
✅ **Lower RAM Usage** - Cloud handles the heavy lifting  

---

## Next Phase Preview

Once Phase 1 is complete and working, Phase 2 will add:
- Wake word detection ("Hey coco") using Porcupine local
- Conversation memory using local SQLite
- coco personality and system prompt tuning
- Persistent session history
- Offline fallback mode (optional)
