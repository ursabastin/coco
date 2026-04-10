import sys
import os
import torch
import time
import whisper
from kokoro_onnx import Kokoro

# Ensure we can import from core
sys.path.append('C:/Users/ursab/coco')

from skills.browser_skill import BrowserSkill
from core.network_monitor import NetworkMonitor
from core.voice_confirmation import VoiceConfirmation

print("="*60)
print("  Network Handling Test")
print("="*60)

# Load models
print("\nLoading models...")
device = "cuda" if torch.cuda.is_available() else "cpu"
stt = whisper.load_model("medium", device=device)
# Updated to match actual files in tts/
tts = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")

# Initialize components
print("Initializing components...")
network = NetworkMonitor()
confirmer = VoiceConfirmation(stt, tts)
browser = BrowserSkill(network_monitor=network, voice_confirmer=confirmer)

# Test 1: Check network speed
print("\n" + "="*60)
print("TEST 1: Network Speed Check")
print("="*60)
result = network.test_network_speed()
print(f"Speed: {result['speed_kbps']:.2f} KB/s")
print(f"Status: {'SLOW' if result['is_slow'] else 'NORMAL'}")
print(f"Recommended timeout: {network.get_recommended_timeout(30)}s")

# Test 2: Open fast site
print("\n" + "="*60)
print("TEST 2: Opening Google (fast site)")
print("="*60)
browser.start_browser()
result = browser.open_website("google")
print(f"Result: {result}")
time.sleep(3)

# Test 3: Open potentially slow site
print("\n" + "="*60)
print("TEST 3: Opening YouTube (may be slow)")
print("="*60)
print("If network is slow, you'll be asked if you want to continue...")
result = browser.open_website("youtube")
print(f"Result: {result}")
time.sleep(3)

# Cleanup
print("\n" + "="*60)
print("Cleaning up...")
browser.close_browser()
network.stop_monitoring()

print("[OK] Test complete!")
print("="*60)
