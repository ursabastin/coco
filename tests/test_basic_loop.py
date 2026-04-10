import sounddevice as sd
import numpy as np
import time
from kokoro_onnx import Kokoro

print("[Test] Loading TTS...")
# Updated to match actual files in tts/
tts = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")

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
    print("[OK] Microphone is working!")
    print("\n[Test] Both audio devices work. The issue is elsewhere.")
else:
    print("[FAIL] Microphone not picking up sound!")
    print("   Check Windows sound settings")
