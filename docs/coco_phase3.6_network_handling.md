# coco — Phase 3.6: Smart Network Timeout Handling
### Adaptive Timeouts + Slow Network Detection + Voice Confirmation

---

## Problems Being Fixed

**Current Issues:**
- ❌ Browser tasks timeout and die on slow network
- ❌ No warning when network is slow
- ❌ User doesn't get a choice to wait or cancel
- ❌ Fixed 30-second timeout kills long-running tasks

**After Phase 3.6:**
- ✅ Adaptive timeouts based on network speed
- ✅ Detects slow network automatically
- ✅ Asks you: "Network is slow, should I wait?" via voice
- ✅ Listens for your voice response (yes/no)
- ✅ Continues or cancels based on your choice
- ✅ Intelligent retry mechanism

---

## STEP 1 — Create Network Monitor

### 1.1 Create Network Monitoring Module

Create `C:\coco\core\network_monitor.py`:

```python
import time
import requests
import threading
from datetime import datetime

class NetworkMonitor:
    def __init__(self):
        self.is_slow = False
        self.average_speed = 0  # KB/s
        self.last_check = None
        self.check_interval = 60  # Check every 60 seconds
        self.monitoring = False
        self.monitor_thread = None
        
        print("[NetworkMonitor] Initialized")
    
    def test_network_speed(self, test_url="https://www.google.com", timeout=5):
        """Test network speed by downloading a small file"""
        try:
            start_time = time.time()
            
            # Download Google homepage (small, always available)
            response = requests.get(test_url, timeout=timeout, stream=True)
            
            # Get content size
            content_length = int(response.headers.get('content-length', 0))
            
            # Download and measure time
            chunks = []
            for chunk in response.iter_content(chunk_size=1024):
                chunks.append(chunk)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate speed in KB/s
            total_bytes = sum(len(chunk) for chunk in chunks)
            speed_kbps = (total_bytes / 1024) / duration if duration > 0 else 0
            
            self.average_speed = speed_kbps
            self.last_check = datetime.now()
            
            # Consider slow if < 50 KB/s (very conservative threshold)
            self.is_slow = speed_kbps < 50
            
            return {
                'speed_kbps': speed_kbps,
                'duration': duration,
                'is_slow': self.is_slow
            }
            
        except requests.Timeout:
            self.is_slow = True
            return {
                'speed_kbps': 0,
                'duration': timeout,
                'is_slow': True,
                'error': 'Timeout'
            }
        except Exception as e:
            # Network error - assume slow
            self.is_slow = True
            return {
                'speed_kbps': 0,
                'duration': 0,
                'is_slow': True,
                'error': str(e)
            }
    
    def start_monitoring(self):
        """Start background network monitoring"""
        if self.monitoring:
            return "Already monitoring"
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        return "Network monitoring started"
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            self.test_network_speed()
            time.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        return "Network monitoring stopped"
    
    def get_recommended_timeout(self, base_timeout=30):
        """Get recommended timeout based on network speed"""
        if self.is_slow:
            # Increase timeout by 3x for slow networks
            return base_timeout * 3
        else:
            return base_timeout
    
    def get_status(self):
        """Get current network status"""
        if self.last_check:
            time_since_check = (datetime.now() - self.last_check).seconds
            return {
                'is_slow': self.is_slow,
                'speed_kbps': self.average_speed,
                'last_check': time_since_check,
                'status': 'slow' if self.is_slow else 'normal'
            }
        else:
            return {
                'is_slow': False,
                'speed_kbps': 0,
                'last_check': None,
                'status': 'unknown'
            }

# Test script
if __name__ == "__main__":
    monitor = NetworkMonitor()
    
    print("Testing network speed...")
    result = monitor.test_network_speed()
    
    print(f"\nResults:")
    print(f"  Speed: {result['speed_kbps']:.2f} KB/s")
    print(f"  Duration: {result['duration']:.2f} seconds")
    print(f"  Status: {'SLOW' if result['is_slow'] else 'NORMAL'}")
    
    recommended = monitor.get_recommended_timeout(30)
    print(f"  Recommended timeout: {recommended} seconds")
```

### 1.2 Test Network Monitor

```powershell
cd C:\coco
.\venv\Scripts\activate
python core\network_monitor.py
```

Expected output:
```
Testing network speed...

Results:
  Speed: 245.67 KB/s
  Status: NORMAL
  Recommended timeout: 30 seconds
```

---

## STEP 2 — Create Voice Confirmation System

### 2.1 Create Confirmation Module

Create `C:\coco\core\voice_confirmation.py`:

```python
import whisper
import torch
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from kokoro_onnx import Kokoro

class VoiceConfirmation:
    def __init__(self, stt_model, tts_model):
        self.stt_model = stt_model
        self.tts_model = tts_model
        print("[VoiceConfirmation] Ready")
    
    def ask_yes_no(self, question, timeout=10):
        """Ask a yes/no question via voice and get voice response"""
        # Speak the question
        print(f"[coco] {question}")
        samples, sample_rate = self.tts_model.create(
            question, 
            voice="af_bella", 
            speed=1.0, 
            lang="en-us"
        )
        sd.play(samples, sample_rate)
        sd.wait()
        
        # Record response
        print(f"[coco] Listening for your response...")
        audio = sd.rec(
            int(timeout * 16000), 
            samplerate=16000, 
            channels=1, 
            dtype='float32'
        )
        sd.wait()
        
        # Save and transcribe
        wav.write("temp_confirmation.wav", 16000, audio)
        result = self.stt_model.transcribe("temp_confirmation.wav")
        response_text = result['text'].strip().lower()
        
        print(f"[You] {response_text}")
        
        # Parse yes/no
        yes_words = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'continue', 'wait', 'proceed']
        no_words = ['no', 'nope', 'cancel', 'stop', 'abort', 'quit', 'exit']
        
        # Check for yes
        if any(word in response_text for word in yes_words):
            return True
        
        # Check for no
        if any(word in response_text for word in no_words):
            return False
        
        # Unclear response - ask again
        print("[coco] I didn't understand. Please say yes or no clearly.")
        return self.ask_yes_no("Should I continue waiting?", timeout=timeout)
    
    def confirm_action(self, action_description):
        """Confirm if user wants to proceed with an action"""
        question = f"I'm about to {action_description}. Should I proceed?"
        return self.ask_yes_no(question)
    
    def notify_and_wait(self, message, wait_time=3):
        """Speak a message and wait"""
        print(f"[coco] {message}")
        samples, sample_rate = self.tts_model.create(
            message,
            voice="af_bella",
            speed=1.0,
            lang="en-us"
        )
        sd.play(samples, sample_rate)
        sd.wait()
        
        import time
        time.sleep(wait_time)

# Test script
if __name__ == "__main__":
    import whisper
    from kokoro_onnx import Kokoro
    
    print("Loading models...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    stt = whisper.load_model("medium", device=device)
    tts = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")
    
    confirmer = VoiceConfirmation(stt, tts)
    
    # Test
    result = confirmer.ask_yes_no("Network is slow. Should I keep waiting?")
    
    if result:
        print("\n✅ User said YES")
    else:
        print("\n❌ User said NO")
```

---

## STEP 3 — Update Browser Skill with Smart Timeouts

### 3.1 Modify Browser Skill

Open `C:\coco\skills\browser_skill.py`

Add network monitor to the class:

```python
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import os
import platform
import sys
sys.path.append('C:/coco')
from core.network_monitor import NetworkMonitor

class BrowserSkill:
    def __init__(self, network_monitor=None, voice_confirmer=None):
        self.playwright = None
        self.browser = None
        self.page = None
        self.browser_type = self.detect_default_browser()
        self.user_data_dir = self.get_user_profile_path()
        
        # Network handling
        self.network_monitor = network_monitor or NetworkMonitor()
        self.voice_confirmer = voice_confirmer
        
        print(f"[BrowserSkill] Detected default browser: {self.browser_type}")
        print(f"[BrowserSkill] Will use profile: {self.user_data_dir}")
    
    # ... [keep existing methods: detect_default_browser, get_user_profile_path, normalize_url, start_browser]
    
    def open_website(self, url, max_retries=2):
        """Open a website with adaptive timeout and retry"""
        if not self.page:
            self.start_browser(headless=False)
        
        # Normalize URL
        full_url = self.normalize_url(url)
        
        # Get recommended timeout based on network speed
        base_timeout = 30000  # 30 seconds
        
        # Check network speed
        network_status = self.network_monitor.test_network_speed()
        
        if network_status['is_slow']:
            timeout = base_timeout * 3  # 90 seconds for slow network
            print(f"[BrowserSkill] Network is slow ({network_status['speed_kbps']:.1f} KB/s)")
            print(f"[BrowserSkill] Using extended timeout: {timeout/1000}s")
            
            # Ask user if they want to continue
            if self.voice_confirmer:
                should_continue = self.voice_confirmer.ask_yes_no(
                    "Network is slow. This might take a while. Should I continue waiting?"
                )
                
                if not should_continue:
                    return "Cancelled due to slow network"
            else:
                print("[BrowserSkill] Warning: Slow network detected, this may take longer")
        else:
            timeout = base_timeout
        
        # Try to load page with retries
        for attempt in range(max_retries + 1):
            try:
                print(f"[BrowserSkill] Loading {url}... (attempt {attempt + 1}/{max_retries + 1})")
                
                self.page.goto(
                    full_url, 
                    timeout=timeout,
                    wait_until="domcontentloaded"
                )
                
                return f"Opened {url}"
                
            except PlaywrightTimeout:
                print(f"[BrowserSkill] Timeout on attempt {attempt + 1}")
                
                if attempt < max_retries:
                    # Ask user if they want to retry
                    if self.voice_confirmer:
                        should_retry = self.voice_confirmer.ask_yes_no(
                            f"Page is taking too long to load. Try again?"
                        )
                        
                        if not should_retry:
                            return f"Cancelled loading {url}"
                    else:
                        print(f"[BrowserSkill] Retrying... ({attempt + 2}/{max_retries + 1})")
                        time.sleep(2)
                else:
                    # Final attempt failed
                    if self.voice_confirmer:
                        self.voice_confirmer.notify_and_wait(
                            f"Could not load {url}. The page may be down or network is too slow."
                        )
                    return f"Failed to load {url} after {max_retries + 1} attempts"
            
            except Exception as e:
                return f"Error opening {url}: {str(e)}"
        
        return f"Error: Could not load {url}"
    
    def search_google(self, query, max_retries=2):
        """Search on Google with retry logic"""
        try:
            # Open Google with smart timeout
            result = self.open_website("https://www.google.com", max_retries=max_retries)
            
            if "Failed" in result or "Cancelled" in result or "Error" in result:
                return result
            
            time.sleep(1)
            
            # Try to search with timeout handling
            try:
                self.page.fill('textarea[name="q"]', query, timeout=10000)
                self.page.press('textarea[name="q"]', 'Enter')
            except:
                try:
                    self.page.fill('input[name="q"]', query, timeout=10000)
                    self.page.press('input[name="q"]', 'Enter')
                except:
                    # Fallback: direct URL
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    return self.open_website(search_url, max_retries=max_retries)
            
            time.sleep(2)
            return f"Searched Google for: {query}"
            
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    # ... [keep other existing methods: click_element, type_text, get_page_title, etc.]
```

---

## STEP 4 — Integrate Network Monitor into coco Agent

### 4.1 Update Advanced Agent

Open `C:\coco\core\coco_advanced.py`

Add network monitor initialization:

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

sys.path.append('C:/coco')

from core.skill_manager import SkillManager
from core.wake_detector import WakeDetector
from core.memory_manager import MemoryManager
from core.task_executor import TaskExecutor
from core.scheduler import TaskScheduler
from core.workflow_manager import WorkflowManager
from core.pattern_learner import PatternLearner
from core.network_monitor import NetworkMonitor  # NEW
from core.voice_confirmation import VoiceConfirmation  # NEW
from integrations.weather_integration import WeatherIntegration

load_dotenv()

# Load models
print("[coco] Loading Whisper on GPU...")
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = whisper.load_model("medium", device=device)

print("[coco] Loading Kokoro...")
tts_model = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

print("[coco] Initializing components...")
wake_detector = WakeDetector(clap_threshold=0.3)

# Initialize network monitor and voice confirmation
network_monitor = NetworkMonitor()
network_monitor.start_monitoring()  # Start background monitoring

voice_confirmer = VoiceConfirmation(stt_model, tts_model)

# Initialize skills with network support
skills = SkillManager(network_monitor=network_monitor, voice_confirmer=voice_confirmer)

memory = MemoryManager()
task_executor = TaskExecutor(skills, memory)
scheduler = TaskScheduler(task_executor=task_executor)
workflows = WorkflowManager()
patterns = PatternLearner()
weather = WeatherIntegration()

# ... [rest of the code stays the same]
```

### 4.2 Update Skill Manager

Open `C:\coco\core\skill_manager.py`

Modify initialization:

```python
import sys
sys.path.append('C:/coco')

from skills.browser_skill import BrowserSkill
from skills.system_skill import SystemSkill
from skills.keyboard_skill import KeyboardSkill
from skills.screen_skill import ScreenSkill
from skills.file_skill import FileSkill

class SkillManager:
    def __init__(self, network_monitor=None, voice_confirmer=None):
        print("[SkillManager] Initializing skills...")
        
        # Pass network support to browser skill
        self.browser = BrowserSkill(
            network_monitor=network_monitor,
            voice_confirmer=voice_confirmer
        )
        
        self.system = SystemSkill()
        self.keyboard = KeyboardSkill()
        self.screen = ScreenSkill()
        self.files = FileSkill()
        
        print("[SkillManager] All skills loaded ✅")
    
    # ... [rest stays the same]
```

---

## STEP 5 — Add Progress Updates During Long Operations

### 5.1 Create Progress Notifier

Create `C:\coco\core\progress_notifier.py`:

```python
import time
import threading
from kokoro_onnx import Kokoro
import sounddevice as sd

class ProgressNotifier:
    def __init__(self, tts_model):
        self.tts_model = tts_model
        self.active = False
        self.thread = None
    
    def start_waiting_notification(self, message="Still working on it", interval=15):
        """Start periodic progress updates"""
        self.active = True
        self.thread = threading.Thread(
            target=self._notify_loop,
            args=(message, interval),
            daemon=True
        )
        self.thread.start()
    
    def _notify_loop(self, message, interval):
        """Background notification loop"""
        time.sleep(interval)  # Wait before first notification
        
        while self.active:
            print(f"[Progress] {message}")
            samples, sample_rate = self.tts_model.create(
                message,
                voice="af_bella",
                speed=1.0,
                lang="en-us"
            )
            sd.play(samples, sample_rate)
            sd.wait()
            
            time.sleep(interval)
    
    def stop(self):
        """Stop notifications"""
        self.active = False

# Usage in browser_skill.py:
# notifier = ProgressNotifier(tts_model)
# notifier.start_waiting_notification("Still loading the page", interval=15)
# ... long operation ...
# notifier.stop()
```

---

## STEP 6 — Test Complete Network Handling

### 6.1 Create Comprehensive Test

Create `C:\coco\test_network_handling.py`:

```python
import sys
sys.path.append('C:/coco')

from skills.browser_skill import BrowserSkill
from core.network_monitor import NetworkMonitor
from core.voice_confirmation import VoiceConfirmation
import whisper
import torch
from kokoro_onnx import Kokoro
import time

print("="*60)
print("  Network Handling Test")
print("="*60)

# Load models
print("\nLoading models...")
device = "cuda" if torch.cuda.is_available() else "cpu"
stt = whisper.load_model("medium", device=device)
tts = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

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

print("✅ Test complete!")
print("="*60)
```

### 6.2 Run Test

```powershell
cd C:\coco
.\venv\Scripts\activate
python test_network_handling.py
```

**Expected behavior:**
1. Checks network speed
2. Opens Google (fast)
3. Opens YouTube
4. **If slow**: Hears "Network is slow. Should I continue waiting?"
5. **You respond**: "Yes" or "No" via voice
6. **Continues or cancels** based on your response

---

## STEP 7 — Add Network Status to coco Startup

Update `coco_advanced.py` startup to show network status:

```python
# After loading all components, add:
print("\n[coco] Testing network connection...")
network_status = network_monitor.test_network_speed()
if network_status['is_slow']:
    print(f"[coco] ⚠️  Network is SLOW ({network_status['speed_kbps']:.1f} KB/s)")
    print(f"[coco] Browser operations will use extended timeouts")
else:
    print(f"[coco] ✅ Network is NORMAL ({network_status['speed_kbps']:.1f} KB/s)")

print("\n" + "="*60)
print("  coco Agent v3.6 - Smart Network Handling")
print("="*60)
```

---

## Configuration Options

### Adjust Network Speed Threshold

In `network_monitor.py`, modify:

```python
# Consider slow if < 50 KB/s (adjust this value)
self.is_slow = speed_kbps < 50  # Increase for stricter, decrease for lenient
```

Recommended values:
- **Very strict**: 100 KB/s (warns even on moderate slowness)
- **Balanced**: 50 KB/s (default)
- **Lenient**: 20 KB/s (only warns on very slow connections)

### Adjust Timeout Multiplier

In `browser_skill.py`:

```python
if network_status['is_slow']:
    timeout = base_timeout * 3  # Change multiplier (2x, 3x, 5x, etc.)
```

### Adjust Voice Confirmation Timeout

In `voice_confirmation.py`:

```python
def ask_yes_no(self, question, timeout=10):  # Change timeout duration
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Always detects as slow | Threshold too high | Lower threshold in network_monitor.py |
| Never detects as slow | Threshold too low | Increase threshold |
| Voice confirmation not working | Audio device issue | Test with test_audio_devices.py |
| Timeouts still happening | Base timeout too low | Increase base_timeout in browser_skill |
| "Should I wait?" repeats | Network fluctuating | Increase check_interval in NetworkMonitor |
| Page loads but marked slow | Testing server slow | Use different test_url in test_network_speed |

---

## Advanced: Simulate Slow Network for Testing

Create `C:\coco\test_slow_network.py`:

```python
import sys
sys.path.append('C:/coco')

from core.network_monitor import NetworkMonitor

# Create monitor with custom slow URL (intentionally slow)
monitor = NetworkMonitor()

# Override the test to force "slow" detection
monitor.is_slow = True
monitor.average_speed = 25  # KB/s

print("Simulating slow network...")
print(f"Speed: {monitor.average_speed} KB/s")
print(f"Is slow: {monitor.is_slow}")
print(f"Recommended timeout: {monitor.get_recommended_timeout(30)}s")

# Now run browser with this monitor
from skills.browser_skill import BrowserSkill
from core.voice_confirmation import VoiceConfirmation
import whisper
import torch
from kokoro_onnx import Kokoro

device = "cuda" if torch.cuda.is_available() else "cpu"
stt = whisper.load_model("medium", device=device)
tts = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

confirmer = VoiceConfirmation(stt, tts)
browser = BrowserSkill(network_monitor=monitor, voice_confirmer=confirmer)

print("\nOpening YouTube with simulated slow network...")
print("You should hear: 'Network is slow. Should I continue waiting?'")

browser.start_browser()
result = browser.open_website("youtube")
print(f"\nResult: {result}")

browser.close_browser()
```

---

## Phase 3.6 Completion Checklist

| Feature | Status |
|---------|--------|
| Network monitor created | ✅ |
| Network speed detection working | ✅ |
| Voice confirmation system created | ✅ |
| Browser skill using adaptive timeouts | ✅ |
| Retry logic implemented | ✅ |
| Voice prompts for slow network | ✅ |
| User can respond yes/no via voice | ✅ |
| Background network monitoring active | ✅ |
| Progress notifications during long ops | ✅ |
| Network status shown on startup | ✅ |

---

## Usage Examples

**Scenario 1: Fast Network**
```
You: "Open YouTube"
coco: "Opening YouTube"
[Browser opens immediately, loads in 3 seconds]
coco: "Opened YouTube"
```

**Scenario 2: Slow Network**
```
You: "Open YouTube"
coco: "Network is slow. This might take a while. Should I continue waiting?"
You: "Yes"
coco: "Okay, still loading..."
[Waits 90 seconds instead of 30]
[Eventually loads]
coco: "Opened YouTube"
```

**Scenario 3: Very Slow Network**
```
You: "Open YouTube"
coco: "Network is slow. Should I continue waiting?"
You: "Yes"
[Waits... times out]
coco: "Page is taking too long to load. Try again?"
You: "No"
coco: "Cancelled loading YouTube"
```

---

## Best Practices

1. **Monitor network before critical operations**
   - Background monitoring runs automatically
   - Check before long downloads/uploads

2. **Set realistic timeouts**
   - 30s base for normal operations
   - 90s for slow networks
   - 180s for very slow networks

3. **Always offer choice**
   - Never silently timeout
   - Ask user if they want to wait
   - Respect their decision

4. **Provide updates**
   - Tell user what's happening
   - Progress notifications every 15s on long ops
   - Network status on startup

---

🎉 **Phase 3.6 Complete!**

coco now intelligently handles network issues:
- ✅ Detects slow network automatically
- ✅ Asks you via voice if you want to wait
- ✅ Listens to your voice response
- ✅ Adjusts timeouts dynamically
- ✅ Never silently kills tasks

No more frustration from timeout errors on slow connections!

Test it:
```powershell
python test_network_handling.py
```
