import pyautogui
import time

print("[Test] Moving mouse to center of screen...")
screen_width, screen_height = pyautogui.size()
pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=1)

print("[Test] Taking screenshot...")
screenshot = pyautogui.screenshot()
screenshot.save("test_screenshot.png")
print("[Test] Screenshot saved as test_screenshot.png")

print("[Test] System control working!")
