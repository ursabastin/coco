import os
import sys
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import requests
from kokoro_onnx import Kokoro
import soundfile as sf
from dotenv import load_dotenv

import torch

# Ensure core and skills can be imported
sys.path.append('c:/Users/ursab/coco')

from core.skill_manager import SkillManager

# Load environment variables
load_dotenv()

# Detect device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[coco] Using device: {device}")

# Load models
print(f"[coco] Loading Whisper ({device})...")
stt_model = whisper.load_model("medium", device=device)

print("[coco] Loading Kokoro...")
# Updated filenames to match actual files in tts/ directory
tts_model = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")

print("[coco] Loading skills...")
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
If yes, provide the action(s) in this format:
ACTION: intent_name | parameter1: value1 | parameter2: value2

You can provide multiple actions, each on a new line starting with ACTION:.

Examples:
User: "Open notepad and type hello"
You: I'll open notepad and type that for you.
ACTION: open_app | app: notepad
ACTION: type_text | text: hello

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
    """Check if response contains one or more actions and execute them"""
    lines = response.split('\n')
    action_found = False
    results = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("ACTION:"):
            action_found = True
            # Parse action
            action_part = line.replace("ACTION:", "").strip()
            parts = [p.strip() for p in action_part.split("|")]
            
            if not parts:
                continue
                
            intent = parts[0]
            parameters = {}
            
            for part in parts[1:]:
                if ":" in part:
                    key, value = part.split(":", 1)
                    parameters[key.strip()] = value.strip()
            
            # Execute via skill manager
            try:
                result = skills.execute_command(intent, parameters)
                results.append(result)
            except Exception as e:
                results.append(f"Error executing {intent}: {str(e)}")
    
    if action_found:
        return True, " ".join(results)
    
    return False, None

# Main Loop
if __name__ == "__main__":
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
