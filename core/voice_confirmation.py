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
    # Updated to match actual files in tts/
    tts = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")
    
    confirmer = VoiceConfirmation(stt, tts)
    
    # Test
    result = confirmer.ask_yes_no("Network is slow. Should I keep waiting?")
    
    if result:
        print("\n[OK] User said YES")
    else:
        print("\n[CANCEL] User said NO")
