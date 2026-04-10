import easyocr
import pyautogui
import os

print("[Test] Loading OCR model (this takes ~30 seconds first time)...")
reader = easyocr.Reader(['en'], gpu=False)

print("[Test] Taking screenshot...")
screenshot = pyautogui.screenshot()
screenshot.save("temp_screen.png")

print("[Test] Reading text from screen...")
results = reader.readtext("temp_screen.png")

print("[Test] Text found on screen:")
for detection in results[:5]:  # Show first 5 results
    print(f"  - {detection[1]}")

if os.path.exists("temp_screen.png"):
    os.remove("temp_screen.png")

print("[Test] OCR working!")
