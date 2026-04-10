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
            try:
                samples, sample_rate = self.tts_model.create(
                    message,
                    voice="af_bella",
                    speed=1.0,
                    lang="en-us"
                )
                sd.play(samples, sample_rate)
                sd.wait()
            except Exception as e:
                print(f"[Progress] Notification error: {e}")
            
            time.sleep(interval)
    
    def stop(self):
        """Stop notifications"""
        self.active = False
