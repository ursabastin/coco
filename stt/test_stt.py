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
