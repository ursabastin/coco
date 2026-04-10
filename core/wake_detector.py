import numpy as np
import sounddevice as sd
import time

class WakeDetector:
    def __init__(self, 
                 clap_threshold=0.3,      # Amplitude threshold for clap detection
                 clap_gap_min=0.1,        # Minimum gap between claps (seconds)
                 clap_gap_max=0.6,        # Maximum gap between claps (seconds)
                 sample_rate=16000):
        
        self.clap_threshold = clap_threshold
        self.clap_gap_min = clap_gap_min
        self.clap_gap_max = clap_gap_max
        self.sample_rate = sample_rate
        
        # Circular buffer for continuous audio monitoring
        self.buffer_duration = 2.0  # Monitor last 2 seconds
        self.buffer_size = int(self.buffer_duration * self.sample_rate)
        self.audio_buffer = np.zeros(self.buffer_size)
        
        print(f"[WakeDetector] Double-clap detection ready")
        print(f"[WakeDetector] Clap threshold: {clap_threshold}")
        print(f"[WakeDetector] Gap range: {clap_gap_min}-{clap_gap_max}s")
    
    def detect_clap(self, audio_chunk):
        """Detect if audio chunk contains a clap (sudden loud sound)"""
        # Calculate RMS (root mean square) amplitude
        rms = np.sqrt(np.mean(audio_chunk**2))
        return rms > self.clap_threshold
    
    def find_claps_in_buffer(self):
        """Find clap timestamps in the audio buffer"""
        # Split buffer into small chunks (50ms each)
        chunk_size = int(0.05 * self.sample_rate)
        num_chunks = len(self.audio_buffer) // chunk_size
        
        clap_times = []
        
        for i in range(num_chunks):
            start = i * chunk_size
            end = start + chunk_size
            chunk = self.audio_buffer[start:end]
            
            if self.detect_clap(chunk):
                time_offset = i * 0.05  # Convert chunk index to time
                clap_times.append(time_offset)
        
        return clap_times
    
    def is_double_clap(self, clap_times):
        """Check if clap pattern matches double-clap"""
        if len(clap_times) < 2:
            return False
        
        # Check for two claps with proper gap
        for i in range(len(clap_times) - 1):
            gap = clap_times[i + 1] - clap_times[i]
            if self.clap_gap_min <= gap <= self.clap_gap_max:
                return True
        
        return False
    
    def listen_for_wake(self, duration=2.0):
        """Listen for double-clap wake signal"""
        # Record audio chunk
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        # Update circular buffer
        audio_flat = audio.flatten()
        self.audio_buffer = np.roll(self.audio_buffer, -len(audio_flat))
        self.audio_buffer[-len(audio_flat):] = audio_flat
        
        # Find claps in buffer
        clap_times = self.find_claps_in_buffer()
        
        # Check for double-clap pattern
        if self.is_double_clap(clap_times):
            return True
        
        return False
    
    def calibrate(self):
        """Help user calibrate clap threshold"""
        print("\n[WakeDetector] Calibration Mode")
        print("We'll measure your clap volume to set the right threshold.")
        print("\nWhen ready, clap TWICE with ~0.3 seconds between claps.")
        input("Press Enter when ready...")
        
        print("\nListening for 3 seconds... CLAP CLAP NOW!")
        audio = sd.rec(
            int(3 * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        # Find max amplitude
        audio_flat = audio.flatten()
        
        # Split into 50ms chunks and find max RMS
        chunk_size = int(0.05 * self.sample_rate)
        num_chunks = len(audio_flat) // chunk_size
        
        max_rms = 0
        for i in range(num_chunks):
            start = i * chunk_size
            end = start + chunk_size
            chunk = audio_flat[start:end]
            rms = np.sqrt(np.mean(chunk**2))
            if rms > max_rms:
                max_rms = rms
        
        # Set threshold to 70% of max clap volume
        suggested_threshold = max_rms * 0.7
        
        print(f"\n[WakeDetector] Detected clap volume: {max_rms:.3f}")
        print(f"[WakeDetector] Suggested threshold: {suggested_threshold:.3f}")
        print(f"\nRecommendation: Set clap_threshold={suggested_threshold:.2f} in wake_detector.py")
        
        return suggested_threshold

# Test script
if __name__ == "__main__":
    detector = WakeDetector()
    
    # Calibration mode
    print("\nDo you want to calibrate? (y/n)")
    if input().lower() == 'y':
        detector.calibrate()
        print("\nRestarting with default settings for testing...")
    
    print("\n[Test] Listening for double-clap...")
    print("[Test] Clap twice quickly to wake coco!")
    print("[Test] Press Ctrl+C to stop\n")
    
    try:
        while True:
            if detector.listen_for_wake(duration=0.5):
                print("[OK] DOUBLE-CLAP DETECTED! coco would wake up now.")
                time.sleep(2)  # Cooldown
    except KeyboardInterrupt:
        print("\n[Test] Stopped")
