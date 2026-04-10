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
try:
    default_input = sd.query_devices(kind='input')['name']
    default_output = sd.query_devices(kind='output')['name']
    print("Current Default Devices:")
    print(f"  Input (Microphone): {default_input}")
    print(f"  Output (Speakers): {default_output}")
except Exception as e:
    print(f"Error getting default devices: {e}")
print()

# Test Input (Microphone)
print("="*60)
print("TEST 1: Microphone Input")
print("="*60)
print("Recording for 3 seconds... SPEAK NOW or CLAP!")
print("(This script will proceed automatically after Enter)")
input("Press Enter to start recording...")

sample_rate = 16000
duration = 3

try:
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    # Calculate volume
    rms = np.sqrt(np.mean(audio**2))
    max_amplitude = np.max(np.abs(audio))
    
    print(f"\n[OK] Recording successful!")
    print(f"   RMS Volume: {rms:.4f}")
    print(f"   Max Amplitude: {max_amplitude:.4f}")
    
    if max_amplitude < 0.01:
        print("\n[WARNING] Very low volume detected!")
        print("   Your microphone might not be working or volume is too low.")
        print("   Check Windows sound settings.")
    else:
        print("\n[OK] Microphone is working!")
        
        # Save recording
        wav.write("test_recording.wav", sample_rate, audio)
        print("   Saved as 'test_recording.wav' - play it to verify")

except Exception as e:
    print(f"\n[ERROR] Recording FAILED: {str(e)}")
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
    
    print("\n[OK] Sound played!")
    heard = input("Did you hear the beep? (y/n): ")
    
    if heard.lower() == 'y':
        print("[OK] Speakers are working!")
    else:
        print("[ERROR] Speakers might not be working")
        print("   Check Windows sound settings and speaker connections")

except Exception as e:
    print(f"\n❌ Playback FAILED: {str(e)}")
    print("   Check if your speakers/headphones are connected")

print()
print("="*60)
print("  Test Complete")
print("="*60)
