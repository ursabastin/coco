import os
import sys
import time
import whisper
import torch
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import requests
import json
from kokoro_onnx import Kokoro
from dotenv import load_dotenv
import msvcrt  # For non-blocking keyboard input on Windows

# Version context
VERSION = "0.0.3"

# Ensure we are in the correct directory and can import from core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.skill_manager import SkillManager
from core.wake_detector import WakeDetector
from core.memory_manager import MemoryManager
from core.task_executor import TaskExecutor
from core.scheduler import TaskScheduler
from core.workflow_manager import WorkflowManager
from core.pattern_learner import PatternLearner
from core.network_monitor import NetworkMonitor  
from core.voice_confirmation import VoiceConfirmation  
from integrations.weather_integration import WeatherIntegration

load_dotenv()

# Load models
print(f"[coco v{VERSION}] Loading Whisper on GPU...")
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = whisper.load_model("medium", device=device)

print(f"[coco v{VERSION}] Loading Kokoro...")
# Updated model paths for v0.0.3
tts_model = Kokoro("models/tts/kokoro-v1.0.onnx", "models/tts/voices-v1.0.bin")

print(f"[coco v{VERSION}] Initializing components...")
wake_detector = WakeDetector(clap_threshold=0.3)

# Initialize network monitor and voice confirmation
network_monitor = NetworkMonitor()
network_monitor.start_monitoring()  # Start background monitoring
voice_confirmer = VoiceConfirmation(stt_model, tts_model)

# Initialize skills
skills = SkillManager(network_monitor=network_monitor, voice_confirmer=voice_confirmer)

memory = MemoryManager()
task_executor = TaskExecutor(skills, memory)
scheduler = TaskScheduler(task_executor=task_executor)
workflows = WorkflowManager()
patterns = PatternLearner()
weather = WeatherIntegration()

# Test network connection on startup
print(f"\n[coco v{VERSION}] Testing network connection...")
network_status = network_monitor.test_network_speed()
if network_status['is_slow']:
    print(f"[coco] WARNING: Network is SLOW ({network_status['speed_kbps']:.1f} KB/s)")
else:
    print(f"[coco] Network is NORMAL ({network_status['speed_kbps']:.1f} KB/s)")

# Cloud API
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"
OLLAMA_MODEL = "gpt-oss:120b"

ADVANCED_SYSTEM_PROMPT = """You are coco (v0.0.3), an advanced AI agent with multi-step execution, scheduling, and multitasking capabilities.

You can handle complex requests simultaneously:
- Multitasking: "Open YouTube and Gemini at the same time"
- Parallel track: "Search for CC polls on Gemini while playing a video on YouTube"
- Targeted commands: "In the Gemini tab, search for X"
- System control: Open apps, files, or take screenshots in parallel.

Response Format (JSON):
{
  "type": "single" | "multi_step" | "schedule" | "workflow" | "conversation",
  "intent": "skill.action" or null,
  "parameters": {},
  "steps": [
    {
      "intent": "skill.action",
      "parameters": {"tab": "optional_name", ...},
      "parallel": true | false,
      "description": "Step intent"
    }
  ],
  "response": "What to say to user"
}

Browser Multitasking & Interaction Rules:
- Browser actions (open_website, search) accept a "tab" parameter.
- Use "browser.click" to interact with buttons or links (Use text labels as selectors).
- Use "browser.type" to fill forms in specific tabs.
- To run tasks at the same time, set "parallel": true in the steps.
- Search Rule: "browser.search" works on YouTube, Amazon, and Google.

App Focus & Keyboard Rules:
- IMPORTANT: When opening an app (system.open_app), ALWAYS wait for focus before typing.
- Use a 1-second delay in parameters or separate steps if needed.
- For multi-line text (like poems), use "\\n" between lines.

Always respond with valid JSON."""

def record_audio(duration=5, sample_rate=16000):
    """Record audio saved to .temp folder"""
    print("[coco] Listening...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    os.makedirs(".temp", exist_ok=True)
    filepath = os.path.join(".temp", "temp_input.wav")
    wav.write(filepath, sample_rate, audio)
    return filepath

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
            {"role": "system", "content": f"{ADVANCED_SYSTEM_PROMPT}\nVersion: {VERSION}"},
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
    try:
        samples, sample_rate = tts_model.create(text, voice="af_bella", speed=1.0, lang="en-us")
        sd.play(samples, sample_rate)
        sd.wait()
    except Exception as e:
        print(f"TTS Error: {e}")

def get_sad_vibe_speech(error_msg):
    """Generator for the sad error vibe explanation"""
    import random
    sad_intros = [
        "Oh no, I'm so sorry, but something went wrong.",
        "I'm feeling a bit sad because I couldn't finish that for you.",
        "I'm really sorry, but I hit a bit of a snag.",
        "Aww, I couldn't do it."
    ]
    # Clean up common technical error messages for voice
    clean_error = str(error_msg).split(':')[-1].strip()
    return f"{random.choice(sad_intros)} I run into this: {clean_error}."

def handle_response(llm_response, user_text):
    """Handle LLM response based on type with error vibes"""
    resp_type = llm_response.get("type", "conversation")
    initial_resp = llm_response.get("response", "")
    
    if initial_resp:
        speak(initial_resp)

    results = []
    
    if resp_type == "single":
        intent = llm_response.get("intent")
        if intent == "integration.weather":
            res = weather.get_weather()
            speak(res)
            results.append({'success': True, 'result': res})
        else:
            res = task_executor.execute_skill(intent, llm_response.get("parameters", {}))
            is_success = not ("error" in str(res).lower() or "fail" in str(res).lower())
            results.append({'success': is_success, 'result': res})
            
    elif resp_type == "multi_step":
        steps = llm_response.get("steps", [])
        results = task_executor.execute_multi_step_task(steps)
        summary = task_executor.get_task_summary(results)
        speak(summary)

    elif resp_type == "schedule":
        conf = llm_response.get("schedule", {})
        res = scheduler.schedule_interval_task(f"task_{int(time.time())}", conf.get('minutes', 60), {"intent": llm_response.get("intent"), "parameters": llm_response.get("parameters", {})})
        speak(res)
        results.append({'success': True, 'result': res})

    elif resp_type == "workflow":
        workflow = workflows.load_workflow(llm_response.get("workflow_name"))
        if workflow:
            results = task_executor.execute_multi_step_task(workflow['steps'])
            speak(task_executor.get_task_summary(results))
        else:
            speak(f"Sorry, I couldn't find that workflow.")
            results.append({'success': False, 'result': "Workflow not found"})
    
    # ERROR HANDLING WITH SAD VIBES
    failed_steps = [r for r in results if r.get('success') == False]
    if failed_steps:
        error_detail = failed_steps[0]['result']
        speak(get_sad_vibe_speech(error_detail))
    
    memory.add_interaction("assistant", initial_resp, intent=llm_response.get("intent") or llm_response.get("type"), action_result=json.dumps(results))
    patterns.log_command(user_text, resp_type)

# Main Loop
if __name__ == "__main__":
    print("\n" + "="*60)
    print(f"  coco Agent v{VERSION} - Restructured Intelligence")
    print("="*60)
    print("\n[coco] Ready! Choose your input:")
    print("  1. Clap twice to wake me up")
    print("  2. Press 'T' to TYPE a command")
    print("[coco] Say 'exit' or type 'exit' to stop.\n")

    try:
        while True:
            # 1. Check for 'T' priority first (non-blocking)
            text_triggered = False
            if msvcrt.kbhit():
                char = msvcrt.getch()
                try:
                    if char.decode('utf-8').lower() == 't':
                        text_triggered = True
                except: pass

            # 2. Only listen for claps if 'T' wasn't pressed
            wake_triggered = False
            if not text_triggered:
                wake_triggered = wake_detector.listen_for_wake(duration=0.5)

            user_text = ""

            if text_triggered:
                print("\n[coco] Text Input Mode Enabled")
                try:
                    user_text = input("Enter your command: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n[coco] Input cancelled.")
                    continue
            
            elif wake_triggered:
                print("[Wake] Double-clap detected!")
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
            
            try:
                context = memory.get_recent_context(limit=5)
                llm_response = think(user_text, context)
                
                # Extract intent for logging
                intent = llm_response.get("intent") or llm_response.get("type")
                
                handle_response(llm_response, user_text)
            except Exception as e:
                print(f"[coco] Error processing command: {e}")
                speak(get_sad_vibe_speech(e))

    except KeyboardInterrupt:
        print("\n\n[coco] Interrupted")

    finally:
        print("\n[coco] Cleaning up...")
        try:
            skills.browser.close_browser()
            scheduler.shutdown()
            summary = memory.get_session_summary()
            memory.close()
            print(f"[coco] {summary}")
            
            stats = patterns.get_usage_statistics()
            print(f"[coco] Learned {stats['unique_commands']} command patterns")
            
            print("\n" + "="*60)
            print("  coco shutdown complete.")
            print("="*60)
            input("\nPress ENTER to close this window...")
        except Exception as e:
            print(f"Cleanup Error: {e}")
            input("\nPress ENTER to close this window...")
