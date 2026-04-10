import pyautogui
import time

class KeyboardSkill:
    def __init__(self):
        # Safety feature - move mouse to corner to abort
        pyautogui.FAILSAFE = True
        # Pause between actions
        pyautogui.PAUSE = 0.1
    
    def type_text(self, text, interval=0.05):
        """Type text with optional interval between keys"""
        pyautogui.write(text, interval=interval)
        return f"Typed: {text}"
    
    def press_key(self, key):
        """Press a single key"""
        pyautogui.press(key)
        return f"Pressed {key}"
    
    def press_hotkey(self, *keys):
        """Press a combination of keys (e.g., ctrl+c)"""
        pyautogui.hotkey(*keys)
        return f"Pressed {'+'.join(keys)}"
    
    def click_at(self, x, y, clicks=1, button='left'):
        """Click at specific coordinates"""
        pyautogui.click(x, y, clicks=clicks, button=button)
        return f"Clicked at ({x}, {y})"
    
    def move_mouse(self, x, y, duration=0.5):
        """Move mouse to coordinates"""
        pyautogui.moveTo(x, y, duration=duration)
        return f"Moved mouse to ({x}, {y})"
    
    def get_mouse_position(self):
        """Get current mouse position"""
        x, y = pyautogui.position()
        return f"Mouse at ({x}, {y})"
    
    def take_screenshot(self, filename="screenshot.png"):
        """Take screenshot"""
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved as {filename}"
    
    def get_screen_size(self):
        """Get screen dimensions"""
        width, height = pyautogui.size()
        return f"Screen size: {width}x{height}"

# Test usage
if __name__ == "__main__":
    kb = KeyboardSkill()
    print(kb.get_screen_size())
    print(kb.get_mouse_position())
