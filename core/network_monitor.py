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
