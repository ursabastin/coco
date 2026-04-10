import easyocr
import pyautogui
import os

class ScreenSkill:
    def __init__(self):
        # Load OCR model (English)
        print("[ScreenSkill] Loading OCR model...")
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("[ScreenSkill] OCR ready")
    
    def read_screen(self):
        """Read all text from current screen"""
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save("temp_screen.png")
        
        # Read text
        results = self.reader.readtext("temp_screen.png")
        
        # Extract text only
        text_list = [detection[1] for detection in results]
        
        # Clean up
        os.remove("temp_screen.png")
        
        return " ".join(text_list) if text_list else "No text found on screen"
    
    def read_region(self, x, y, width, height):
        """Read text from specific screen region"""
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save("temp_region.png")
        
        results = self.reader.readtext("temp_region.png")
        text_list = [detection[1] for detection in results]
        
        os.remove("temp_region.png")
        
        return " ".join(text_list) if text_list else "No text found in region"

# Test usage
if __name__ == "__main__":
    screen = ScreenSkill()
    print(screen.read_screen())
