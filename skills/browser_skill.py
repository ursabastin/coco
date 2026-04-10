from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import os
import platform
import sys
import threading
import urllib.parse

# Ensure we can import from core
sys.path.append('C:/Users/ursab/coco')
from core.network_monitor import NetworkMonitor

class BrowserSkill:
    def __init__(self, network_monitor=None, voice_confirmer=None):
        self.playwright = None
        self.browser = None
        self.pages = {}  # Dictionary to store named tabs/pages
        self.current_tab = "default"
        
        # FORCING CHROME
        self.browser_type = "chrome" 
        self.user_data_dir = self.get_user_profile_path()
        
        # Network handling
        self.network_monitor = network_monitor or NetworkMonitor()
        self.voice_confirmer = voice_confirmer
        
        print(f"[BrowserSkill] Forced Browser: {self.browser_type}")
        print(f"[BrowserSkill] Using Profile Path: {self.user_data_dir}")
    
    def get_user_profile_path(self):
        home = os.path.expanduser("~")
        if platform.system() == "Windows":
             return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
        return None
    
    def normalize_url(self, url_or_name):
        url_lower = url_or_name.lower().strip()
        site_mappings = {
            'youtube': 'youtube.com', 'google': 'google.com', 'gmail': 'mail.google.com',
            'gemini': 'gemini.google.com', 'chatgpt': 'chatgpt.com',
            'github': 'github.com', 'amazon': 'amazon.com', 'canva': 'canva.com'
        }
        for name, domain in site_mappings.items():
            if name in url_lower and '.' not in url_lower:
                return f"https://{domain}"
        if url_lower.startswith(('http://', 'https://')): return url_or_name
        if '.' in url_lower: return f"https://{url_or_name}"
        return f"https://www.google.com/search?q={url_or_name}"

    def get_page(self, tab_name="default"):
        if not self.playwright:
            res = self.start_browser()
            if "Error" in str(res): return None
        if not self.browser: return None
        if tab_name not in self.pages or self.pages[tab_name].is_closed():
            print(f"[BrowserSkill] Creating tab: {tab_name}")
            try:
                self.pages[tab_name] = self.browser.new_page()
            except:
                if hasattr(self.browser, "new_page"): self.pages[tab_name] = self.browser.new_page()
        return self.pages[tab_name]

    def start_browser(self, headless=False):
        if self.playwright: return "Browser already running"
        try:
            self.playwright = sync_playwright().start()
            args = ['--no-sandbox', '--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check']
            profile_dir = "Default"
            
            if self.user_data_dir and os.path.exists(self.user_data_dir):
                print(f"[BrowserSkill] Opening Chrome profile [{profile_dir}]...")
                try:
                    self.browser = self.playwright.chromium.launch_persistent_context(
                        user_data_dir=self.user_data_dir,
                        headless=headless,
                        args=args + [f"--profile-directory={profile_dir}"],
                        channel="chrome"
                    )
                    page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
                    self.pages["default"] = page
                    return f"Browser started with Chrome profile: {profile_dir}"
                except:
                    print(f"[BrowserSkill] Profile locked. Using Safe fallback.")
            
            # Use Local Temp for fallback (avoids profile picker)
            temp_dir = os.path.join(os.getcwd(), ".coco_chrome_temp")
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=temp_dir, headless=headless, args=args, channel="chrome"
            )
            page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
            self.pages["default"] = page
            return "Chrome started (Safe/Guest mode)"
        except Exception as e:
            self.playwright = None
            return f"Error: {e}"

    def open_website(self, url, tab_name="default"):
        page = self.get_page(tab_name)
        if not page: return "Error: Browser not ready"
        full_url = self.normalize_url(url)
        timeout = 90000 if self.network_monitor.test_network_speed()['is_slow'] else 30000
        try:
            print(f"[BrowserSkill] Tab [{tab_name}] -> {full_url}")
            page.goto(full_url, timeout=timeout, wait_until="domcontentloaded")
            return f"Opened {url}"
        except Exception as e: return f"Load error: {e}"

    def search_in_tab(self, query, tab_name="default"):
        """Smarter search that stays on the current site if possible"""
        page = self.get_page(tab_name)
        if not page: return "Error"
        
        q_enc = urllib.parse.quote(query)
        current_url = page.url.lower()
        
        # Site-specific direct search (Faster and more reliable)
        if "youtube.com" in current_url:
            target = f"https://www.youtube.com/results?search_query={q_enc}"
        elif "amazon.com" in current_url:
            target = f"https://www.amazon.com/s?k={q_enc}"
        elif "github.com" in current_url:
            target = f"https://github.com/search?q={q_enc}"
        else:
            target = f"https://www.google.com/search?q={q_enc}"
        
        return self.open_website(target, tab_name)

    def click_element(self, selector, tab_name="default"):
        """Click on a specific element by text or selector"""
        page = self.get_page(tab_name)
        try:
            # Try text-based click first for "Interact" commands
            if not selector.startswith('.') and not selector.startswith('#'):
                page.get_by_text(selector).first.click(timeout=5000)
            else:
                page.click(selector, timeout=5000)
            return f"Clicked {selector}"
        except:
            return f"Could not find or click {selector}"

    def type_in_element(self, selector, text, tab_name="default"):
        page = self.get_page(tab_name)
        try:
            page.fill(selector, text, timeout=5000)
            return f"Entered text in {selector}"
        except:
            return f"Could not find {selector}"

    def close_browser(self):
        try:
            if self.browser: self.browser.close()
            if self.playwright: self.playwright.stop()
            self.pages = {}
            self.playwright = None
        except: pass
