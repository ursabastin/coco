# coco — Phase 1: Foundation Setup
### Google Antigravity Build Instructions

---

## Prerequisites Before Starting

Make sure you have the following ready:
- Windows 11 (you have it ✅)
- At least 20GB free on C: drive
- Internet connection (only needed during setup/download phase)
- A Google account (for Antigravity sign-in)

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

## STEP 3 — Install Ollama (Local LLM)

### 3.1 Download Ollama
Go to: `https://ollama.com/download`
Download and run the **Windows installer**.

### 3.2 Verify Installation
Open a **new PowerShell window** and run:

```powershell
ollama --version
```

Expected output: `ollama version 0.x.x`

### 3.3 Download Phi-3 Mini Model
This is your LLM brain. Run:

```powershell
ollama pull phi3:mini
```

This downloads ~2.3GB. Wait for it to complete.

### 3.4 Test Ollama
```powershell
ollama run phi3:mini "Say hello as coco assistant"
```

Expected: A short response from the model. If you get a response → ✅ Ollama is working.

### 3.5 Run Ollama as Background Service
```powershell
ollama serve
```

Keep this PowerShell window open. Ollama runs on `http://localhost:11434`.

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

This downloads ~1.5GB. This runs on **CPU** to save VRAM for Ollama.

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

text = "Hello. I am coco. Your fully local AI assistant. I am ready."
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

## STEP 6 — Connect All Three Together

### 6.1 Install Requests Library

```powershell
pip install requests
```

### 6.2 Create Core Loop
Create `C:\coco\core\coco_core.py`:

```python
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import requests
from kokoro_onnx import Kokoro
import soundfile as sf

# Load models
print("[coco] Loading Whisper...")
stt_model = whisper.load_model("medium")

print("[coco] Loading Kokoro...")
tts_model = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:mini"

SYSTEM_PROMPT = """You are coco, a fully local AI assistant running on the user's laptop.
You are helpful, concise, and smart. Keep responses short and clear.
Never mention being an AI unless asked."""

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
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\nUser: {user_input}\ncoco:",
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()['response'].strip()

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

### 6.3 Save Requirements
Create `C:\coco\requirements.txt`:

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
```

---

## STEP 7 — First Full Test

### 7.1 Make Sure Ollama is Running
In a separate PowerShell window:

```powershell
ollama serve
```

### 7.2 Activate Venv and Run coco
In Antigravity terminal:

```powershell
cd C:\coco
.\venv\Scripts\activate
python core\coco_core.py
```

### 7.3 Expected Startup Output

```
[coco] Loading Whisper...
[coco] Loading Kokoro...
[coco] Ready. Starting interaction loop...
[coco] coco is ready. How can I help you?
[coco] Listening...
```

Speak something. coco should transcribe → think → respond with voice.

---

## Phase 1 Completion Checklist

| Task | Status |
|------|--------|
| Antigravity installed & project opened | ✅ |
| Python venv created and active | ✅ |
| Ollama installed + Phi-3 Mini downloaded | ✅ |
| Ollama responding to prompts | ✅ |
| Whisper installed + FFmpeg installed | ✅ |
| Whisper transcribing voice correctly | ✅ |
| Kokoro installed + model files downloaded | ✅ |
| Kokoro speaking audio correctly | ✅ |
| Full core loop running end-to-end | ✅ |

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `ollama: command not found` | Restart PowerShell after Ollama install |
| `ffmpeg not found` | Re-add to PATH and restart terminal |
| `No module named 'whisper'` | Make sure venv is active: `.\venv\Scripts\activate` |
| `Connection refused` on Ollama | Run `ollama serve` in a separate window |
| `pyaudio install failed` | Use `pipwin install pyaudio` instead |
| Whisper very slow | Normal on first run — model is loading into memory |

---

## Next Phase Preview

Once Phase 1 is complete and working, Phase 2 will add:
- Wake word detection ("Hey coco") using Porcupine local
- Conversation memory using local SQLite
- coco personality and system prompt tuning
- Persistent session history
