from skills.browser_skill import BrowserSkill
import time

print("Testing browser with real profile...\n")

browser = BrowserSkill()

print("1. Starting browser...")
print(browser.start_browser())
time.sleep(2)

print("\n2. Opening YouTube...")
print(browser.open_website("youtube"))
time.sleep(3)

print("\n3. Opening Google...")
print(browser.open_website("google"))
time.sleep(3)

print("\n4. Searching...")
print(browser.search_google("coco AI assistant"))
time.sleep(3)

print("\n5. Closing browser...")
print(browser.close_browser())

print("\n✅ Test complete!")
print("\nDid you see:")
print("  - Your default browser opened?")
print("  - You were logged in to YouTube/Google?")
print("  - All sites loaded correctly?")
