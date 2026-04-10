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
# Updated to match actual files in tts/
tts_model = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")

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
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
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

def execute_skill(intent, parameters, memory=None):
    """Execute skill based on intent"""
    if not intent or intent == "null":
        return None
    
    try:
        # Parse skill.action format
        if "." in intent:
            skill_name, action_name = intent.split(".")
        else:
            return f"Invalid intent format: {intent}"
        
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
                # Handle context mapping from memory if needed
                app_name = parameters.get('app', '')
                if (not app_name or app_name == 'it') and memory:
                     last_app = memory.get_last_mentioned_entity("app")
                     if last_app:
                         app_name = last_app
                return skills.system.close_application(app_name)
            elif action_name == "list_apps":
                apps = skills.system.list_running_apps()
                return f"Running apps: {', '.join(apps[:10])}"
            elif action_name == "minimize_window":
                return skills.system.minimize_window(parameters.get('title', ''))
            elif action_name == "maximize_window":
                return skills.system.maximize_window(parameters.get('title', ''))
        
        elif skill_name == "keyboard":
            if action_name == "type_text":
                return skills.keyboard.type_text(parameters.get('text', ''))
            elif action_name == "press_key":
                return skills.keyboard.press_key(parameters.get('key', ''))
            elif action_name == "press_hotkey":
                return skills.keyboard.press_hotkey(*parameters.get('keys', []))
            elif action_name == "click_at":
                return skills.keyboard.click_at(parameters.get('x'), parameters.get('y'))
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
            elif action_name == "read_file":
                return skills.files.read_file(parameters.get('filepath', ''))
            elif action_name == "delete_file":
                return skills.files.delete_file(parameters.get('filepath', ''))
            elif action_name == "list_files":
                files = skills.files.list_files(parameters.get('folder', '.'))
                return f"Files: {', '.join(files[:15])}"
        
        return f"Unknown skill action: {intent}"
    
    except Exception as e:
        return f"Error executing skill: {str(e)}"

# Main Loop
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  coco Agent v2.5 - Double-Clap Wake Enabled")
    print("="*50)
    print("\n[coco] Ready! Clap twice to wake me up.")
    print("[coco] Say 'exit' or 'shutdown coco' to stop.\n")
    
    try:
        while True:
            # Wait for double-clap wake signal
            if wake_detector.listen_for_wake(duration=0.5):
                print("!! [Wake] Double-clap detected!")
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
                    # Handle context mapping for "it"/null parameters
                    intent = llm_response["intent"]
                    params = llm_response.get("parameters", {})
                    
                    action_result = execute_skill(
                        intent,
                        params,
                        memory=memory
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
        if hasattr(skills, 'browser'):
            skills.browser.close_browser()
        memory.close()
        print("[coco] Session ended")
        print(f"[coco] {memory.get_session_summary()}")
