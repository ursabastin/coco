# coco Phase 3 — Audio & Wake Detection Troubleshooting
### Fixing "Nothing Works" After Successful Startup

---

## The Problem

coco loads successfully:
```
[coco] Ready! Clap twice to wake me up.
```

But then **nothing happens**:
- ❌ Clapping doesn't wake coco
- ❌ No voice response
- ❌ No recognition

---

## Root Cause

**Audio device configuration issue.** Windows has multiple audio devices and coco doesn't know which one to use.

---

## SOLUTION 1 — Test Audio Devices (Do This First!)

### 1.1 Create Audio Device Tester

Create `C:\coco\core\test_audio_devices.py`:

```python
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

print("="*60)
print("  Audio Device Tester for coco")
print("="*60)
print()

# List all audio devices
print("Available Audio Devices:")
print(sd.query_devices())
print()

# Get default devices
print("Current Default Devices:")
print(f"  Input (Microphone): {sd.query_devices(kind='input')['name']}")
print(f"  Output (Speakers): {sd.query_devices(kind='output')['name']}")
print()

# Test Input (Microphone)
print("="*60)
print("TEST 1: Microphone Input")
print("="*60)
print("Recording for 3 seconds... SPEAK NOW or CLAP!")
input("Press Enter to start recording...")

sample_rate = 16000
duration = 3

try:
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    # Calculate volume
    rms = np.sqrt(np.mean(audio**2))
    max_amplitude = np.max(np.abs(audio))
    
    print(f"\n✅ Recording successful!")
    print(f"   RMS Volume: {rms:.4f}")
    print(f"   Max Amplitude: {max_amplitude:.4f}")
    
    if max_amplitude < 0.01:
        print("\n⚠️  WARNING: Very low volume detected!")
        print("   Your microphone might not be working or volume is too low.")
        print("   Check Windows sound settings.")
    else:
        print("\n✅ Microphone is working!")
        
        # Save recording
        wav.write("test_recording.wav", sample_rate, audio)
        print("   Saved as 'test_recording.wav' - play it to verify")

except Exception as e:
    print(f"\n❌ Recording FAILED: {str(e)}")
    print("   Check if your microphone is connected and enabled")

print()

# Test Output (Speakers)
print("="*60)
print("TEST 2: Speaker Output")
print("="*60)
print("Playing test tone... You should hear a beep!")
input("Press Enter to play sound...")

try:
    # Generate 1-second beep at 440Hz
    frequency = 440
    duration = 1
    t = np.linspace(0, duration, int(sample_rate * duration))
    beep = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    sd.play(beep, sample_rate)
    sd.wait()
    
    print("\n✅ Sound played!")
    heard = input("Did you hear the beep? (y/n): ")
    
    if heard.lower() == 'y':
        print("✅ Speakers are working!")
    else:
        print("❌ Speakers might not be working")
        print("   Check Windows sound settings and speaker connections")

except Exception as e:
    print(f"\n❌ Playback FAILED: {str(e)}")
    print("   Check if your speakers/headphones are connected")

print()
print("="*60)
print("  Test Complete")
print("="*60)
```

### 1.2 Run the Test

```powershell
cd C:\coco
.\venv\Scripts\activate
python core\test_audio_devices.py
```

### 1.3 Check Results

**If microphone test shows low volume (<0.01):**
- Go to Windows Settings → System → Sound
- Check "Input device" and increase microphone volume
- Test microphone using Windows "Test your microphone"

**If speaker test doesn't play:**
- Go to Windows Settings → System → Sound
- Check "Output device" is correct
- Increase volume

---

## SOLUTION 2 — Calibrate Wake Detector

The default `clap_threshold=0.3` might be wrong for your environment.

### 2.1 Run Calibration

```powershell
python core\wake_detector.py
```

### 2.2 Follow Calibration Steps

1. Type `y` when asked "Do you want to calibrate?"
2. Press Enter
3. **Clap twice** when prompted (0.3 seconds apart)
4. Note the suggested threshold

Example output:
```
Detected clap volume: 0.542
Suggested threshold: 0.38
```

### 2.3 Update Threshold

Open `C:\coco\core\coco_advanced.py` and find this line:
```python
wake_detector = WakeDetector(clap_threshold=0.3)
```

Change `0.3` to your suggested value:
```python
wake_detector = WakeDetector(clap_threshold=0.38)  # Use your value!
```

Save and try again.

---

## SOLUTION 3 — Specify Audio Devices Manually

If Windows has multiple microphones/speakers, tell coco which to use.

### 3.1 List Your Devices

```powershell
python -c "import sounddevice; print(sounddevice.query_devices())"
```

Output example:
```
  0 Microphone Array (Intel), MME (2 in, 0 out)
> 1 Headset Microphone (Realtek), MME (1 in, 0 out)
  2 Speakers (Intel), MME (0 in, 2 out)
< 3 Headphones (Realtek), MME (0 in, 2 out)
```

The `>` shows default input (microphone)  
The `<` shows default output (speakers)

### 3.2 Set Specific Device

If you want to use device #1 for input and #3 for output:

Open `C:\coco\core\coco_advanced.py`

Find the `record_audio` function and add `device` parameter:
```python
def record_audio(duration=5, sample_rate=16000):
    """Record audio"""
    print("[coco] Listening...")
    audio = sd.rec(
        int(duration * sample_rate), 
        samplerate=sample_rate, 
        channels=1, 
        dtype='float32',
        device=1  # ADD THIS - Use your input device number
    )
    sd.wait()
    wav.write("temp_input.wav", sample_rate, audio)
    return "temp_input.wav"
```

Find the `speak` function and add `device` parameter:
```python
def speak(text):
    """Speak text"""
    print(f"[coco] {text}")
    samples, sample_rate = tts_model.create(text, voice="af_bella", speed=1.0, lang="en-us")
    sd.play(
        samples, 
        sample_rate,
        device=3  # ADD THIS - Use your output device number
    )
    sd.wait()
```

Also update `wake_detector.py` in the `WakeDetector.listen_for_wake` method:
```python
def listen_for_wake(self, duration=2.0):
    """Listen for double-clap wake signal"""
    audio = sd.rec(
        int(duration * self.sample_rate),
        samplerate=self.sample_rate,
        channels=1,
        dtype='float32',
        device=1  # ADD THIS - Use your input device number
    )
    sd.wait()
    # ... rest of code
```

---

## SOLUTION 4 — Test Each Component Separately

### 4.1 Test Wake Detector Only

```powershell
python core\wake_detector.py
```

Skip calibration (type `n`), then clap twice. Should see:
```
✅ DOUBLE-CLAP DETECTED!
```

If this doesn't work → wake detection issue (try calibration)

### 4.2 Test TTS Only

```powershell
python tts\test_tts.py
```

Should hear coco speak. If not → speaker issue

### 4.3 Test STT Only

```powershell
python stt\test_stt.py
```

Should transcribe your voice. If not → microphone issue

---

## SOLUTION 5 — Simplified Test Script

Create `C:\coco\core\test_basic_loop.py`:

```python
import sounddevice as sd
import numpy as np
import time
from kokoro_onnx import Kokoro

print("[Test] Loading TTS...")
tts = Kokoro("tts/kokoro-v0_19.onnx", "tts/voices.bin")

print("[Test] Testing speaker output...")
samples, sample_rate = tts.create("Testing coco audio. Can you hear me?", voice="af_bella", speed=1.0, lang="en-us")
sd.play(samples, sample_rate)
sd.wait()

print("\n[Test] Now testing microphone input...")
print("[Test] Recording for 3 seconds... Say something!")
time.sleep(1)

audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='float32')
sd.wait()

rms = np.sqrt(np.mean(audio**2))
print(f"[Test] Recording complete. Volume: {rms:.4f}")

if rms > 0.01:
    print("✅ Microphone is working!")
    print("\n[Test] Both audio devices work. The issue is elsewhere.")
else:
    print("❌ Microphone not picking up sound!")
    print("   Check Windows sound settings")
```

Run:
```powershell
python core\test_basic_loop.py
```

---

## Common Issues & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Program loads but silent | Wrong audio devices | Run test_audio_devices.py |
| Clapping doesn't wake | Threshold too high | Run calibration |
| Wake works but no voice | Output device wrong | Check speakers in Windows |
| Wake works but can't hear you | Input device wrong | Check microphone in Windows |
| "Buffer overflow" errors | Sample rate mismatch | Check device supports 16000Hz |
| Intermittent wake detection | Background noise | Increase threshold or reduce noise |

---

## Quick Diagnostic Checklist

Run these in order:

```powershell
# 1. Check audio devices
python core\test_audio_devices.py

# 2. Calibrate wake detector
python core\wake_detector.py

# 3. Test TTS
python tts\test_tts.py

# 4. Test STT  
python stt\test_stt.py

# 5. Test basic loop
python core\test_basic_loop.py

# 6. If all pass, try coco again
python core\coco_advanced.py
```

---

## Windows Sound Settings Quick Fix

### Set Default Devices

1. Right-click speaker icon in taskbar
2. Click "Sound settings"
3. Under "Input", select your microphone
4. Click "Test your microphone" - speak and see if bar moves
5. Under "Output", select your speakers
6. Click "Test" - should hear sound

### Increase Microphone Volume

1. Sound settings → Input device → Device properties
2. Set volume to 80-100%
3. Click "Additional device properties"
4. Levels tab → Set microphone to 80-100%
5. Click OK

---

## Still Not Working?

If you've tried everything and it still doesn't work, run this diagnostic:

```powershell
python -c "import sounddevice as sd; import torch; print('Audio devices:', sd.query_devices()); print('CUDA available:', torch.cuda.is_available())"
```

Copy the output and we can diagnose further.

---

## Expected Working Behavior

When everything is configured correctly:

1. Start coco: `python core\coco_advanced.py`
2. See: `[coco] Ready! Clap twice to wake me up.`
3. **Clap twice quickly** (0.3s apart)
4. See: `👏👏 [Wake] Double-clap detected!`
5. Hear: "Yes?" from speakers
6. See: `[coco] Listening...`
7. **Speak your command**
8. See: `[You] your transcribed text`
9. Hear: coco's response
10. Action executes

If any step fails, go back to the specific test for that component.
