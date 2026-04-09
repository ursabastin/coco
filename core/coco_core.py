#!C:\Users\ursab\coco\venv\Scripts\python.exe
import os
import sys

# Auto-inject virtual environment packages if run outside venv
venv_site_packages = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv', 'Lib', 'site-packages'))
if venv_site_packages not in sys.path and os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

# Auto-inject FFmpeg to PATH so Whisper doesn't fail
ffmpeg_path = r"C:\Users\ursab\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
if ffmpeg_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")

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
print("[coco] Loading Whisper (GPU)...")
stt_model = whisper.load_model("medium", device="cuda")

print("[coco] Loading Kokoro (GPU)...")
tts_model = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")
# kokoro-onnx 0.5.0+ allows setting providers via the session
# But by default it should pick up CUDA if onnxruntime-gpu is installed.
# We will verify this by checking the session providers if needed.

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
    result = stt_model.transcribe(audio_path, fp16=True)
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
