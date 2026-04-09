from kokoro_onnx import Kokoro
import soundfile as sf
import sounddevice as sd

kokoro = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")

text = "Hello. I am coco. Your fully local AI assistant. I am ready."
samples, sample_rate = kokoro.create(text, voice="af_bella", speed=1.0, lang="en-us")

print("Playing response...")
sd.play(samples, sample_rate)
sd.wait()
print("Done.")
