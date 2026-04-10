from playwright.sync_api import sync_playwright
import time

print("[Test] Starting Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    print("[Test] Opening Google...")
    page.goto("https://www.google.com")
    
    print("[Test] Searching for 'coco AI assistant'...")
    page.fill('textarea[name="q"]', 'coco AI assistant')
    page.press('textarea[name="q"]', 'Enter')
    
    time.sleep(3)
    print("[Test] Search complete!")
    
    browser.close()
    print("[Test] Playwright working!")
