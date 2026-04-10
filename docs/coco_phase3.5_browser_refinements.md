# coco — Phase 3.5: Browser & Execution Refinements
### Fix Action Execution + Use Default Browser + Real Profile

---

## Problems Being Fixed

**Current Issues:**
- ❌ coco says "opening YouTube" but nothing opens
- ❌ Browser opens in guest/incognito mode (no saved logins)
- ❌ Uses hardcoded Chromium instead of your default browser
- ❌ URL parsing doesn't understand "open YouTube" → should open youtube.com

**After Phase 3.5:**
- ✅ Actions actually execute (YouTube opens!)
- ✅ Uses YOUR default browser (Chrome/Edge/Firefox)
- ✅ Uses YOUR real profile (saved passwords, history, bookmarks)
- ✅ Smart URL parsing ("open YouTube" → youtube.com)

---

## STEP 1 — Fix Browser Skill Execution

### 1.1 Identify the Problem

Open `C:\coco\core\coco_advanced.py` and look at the `handle_response` function.

The issue: When `response_type == "single"`, it calls `task_executor.execute_skill()` but browser actions aren't in the task_executor!

### 1.2 Update Browser Skill

Open `C:\coco\skills\browser_skill.py` and **REPLACE ENTIRELY** with this improved version:

```python
from playwright.sync_api import sync_playwright
import time
import os
import platform

class BrowserSkill:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.browser_type = self.detect_default_browser()
        self.user_data_dir = self.get_user_profile_path()
        
        print(f"[BrowserSkill] Detected default browser: {self.browser_type}")
        print(f"[BrowserSkill] Will use profile: {self.user_data_dir}")
    
    def detect_default_browser(self):
        """Detect system default browser"""
        system = platform.system()
        
        if system == "Windows":
            import winreg
            try:
                # Check default browser from registry
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                    r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice")
                prog_id = winreg.QueryValueEx(key, "ProgId")[0]
                winreg.CloseKey(key)
                
                if "Chrome" in prog_id:
                    return "chrome"
                elif "Edge" in prog_id or "MSEdge" in prog_id:
                    return "msedge"
                elif "Firefox" in prog_id:
                    return "firefox"
                else:
                    return "chrome"  # Default fallback
            except:
                return "chrome"  # Fallback
        
        return "chrome"  # Default for non-Windows
    
    def get_user_profile_path(self):
        """Get user's browser profile path"""
        system = platform.system()
        home = os.path.expanduser("~")
        
        if system == "Windows":
            if self.browser_type == "chrome":
                return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
            elif self.browser_type == "msedge":
                return os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data")
            elif self.browser_type == "firefox":
                # Firefox uses profiles differently - will handle separately
                return None
        
        return None
    
    def normalize_url(self, url_or_name):
        """Convert natural language to proper URL"""
        url_lower = url_or_name.lower().strip()
        
        # Common site mappings
        site_mappings = {
            'youtube': 'youtube.com',
            'google': 'google.com',
            'gmail': 'gmail.com',
            'facebook': 'facebook.com',
            'twitter': 'twitter.com',
            'x': 'twitter.com',
            'instagram': 'instagram.com',
            'reddit': 'reddit.com',
            'linkedin': 'linkedin.com',
            'github': 'github.com',
            'stackoverflow': 'stackoverflow.com',
            'amazon': 'amazon.com',
            'netflix': 'netflix.com',
            'spotify': 'spotify.com',
        }
        
        # Check if it's a known site name
        for name, domain in site_mappings.items():
            if name in url_lower and '.' not in url_lower:
                return f"https://{domain}"
        
        # If already has protocol, use as-is
        if url_lower.startswith('http://') or url_lower.startswith('https://'):
            return url_or_name
        
        # If has domain extension, add https
        if '.' in url_lower:
            return f"https://{url_or_name}"
        
        # Otherwise, search Google for it
        return f"https://www.google.com/search?q={url_or_name}"
    
    def start_browser(self, headless=False):
        """Launch browser with user profile"""
        if self.playwright:
            return "Browser already running"
        
        self.playwright = sync_playwright().start()
        
        # Browser launch arguments
        launch_args = {
            'headless': headless,
            'args': [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
        }
        
        # Add user data directory if available (Chrome/Edge only)
        if self.user_data_dir and os.path.exists(self.user_data_dir):
            # Use persistent context for Chrome/Edge
            if self.browser_type == "chrome":
                self.browser = self.playwright.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=headless,
                    args=launch_args['args'],
                    channel="chrome"  # Use installed Chrome
                )
                self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
            elif self.browser_type == "msedge":
                self.browser = self.playwright.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=headless,
                    args=launch_args['args'],
                    channel="msedge"  # Use installed Edge
                )
                self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
            else:
                # Fallback for other browsers
                self.browser = self.playwright.chromium.launch(**launch_args)
                self.page = self.browser.new_page()
        else:
            # No user profile - use default
            if self.browser_type == "chrome":
                self.browser = self.playwright.chromium.launch(channel="chrome", **launch_args)
            elif self.browser_type == "msedge":
                self.browser = self.playwright.chromium.launch(channel="msedge", **launch_args)
            else:
                self.browser = self.playwright.chromium.launch(**launch_args)
            
            self.page = self.browser.new_page()
        
        return f"Browser started ({self.browser_type})"
    
    def open_website(self, url):
        """Open a website"""
        if not self.page:
            self.start_browser(headless=False)
        
        # Normalize URL
        full_url = self.normalize_url(url)
        
        try:
            self.page.goto(full_url, timeout=30000, wait_until="domcontentloaded")
            return f"Opened {url}"
        except Exception as e:
            return f"Error opening {url}: {str(e)}"
    
    def search_google(self, query):
        """Search on Google"""
        try:
            self.open_website("https://www.google.com")
            time.sleep(1)
            
            # Try different Google search selectors
            try:
                self.page.fill('textarea[name="q"]', query)
                self.page.press('textarea[name="q"]', 'Enter')
            except:
                try:
                    self.page.fill('input[name="q"]', query)
                    self.page.press('input[name="q"]', 'Enter')
                except:
                    # Fallback: direct URL
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    self.page.goto(search_url)
            
            time.sleep(2)
            return f"Searched Google for: {query}"
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    def click_element(self, selector):
        """Click an element by CSS selector"""
        if not self.page:
            return "No browser open"
        try:
            self.page.click(selector, timeout=5000)
            return f"Clicked {selector}"
        except Exception as e:
            return f"Error clicking: {str(e)}"
    
    def type_text(self, selector, text):
        """Type text into an element"""
        if not self.page:
            return "No browser open"
        try:
            self.page.fill(selector, text)
            return f"Typed text into {selector}"
        except Exception as e:
            return f"Error typing: {str(e)}"
    
    def get_page_title(self):
        """Get current page title"""
        if not self.page:
            return "No browser open"
        try:
            return self.page.title()
        except:
            return "Could not get title"
    
    def get_page_text(self):
        """Get visible text from page"""
        if not self.page:
            return "No browser open"
        try:
            return self.page.inner_text('body')[:500]  # First 500 chars
        except:
            return "Could not get page text"
    
    def take_screenshot(self, filename="screenshot.png"):
        """Take screenshot of current page"""
        if not self.page:
            return "No browser open"
        try:
            self.page.screenshot(path=filename)
            return f"Screenshot saved as {filename}"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"
    
    def close_browser(self):
        """Close the browser"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.browser = None
            self.page = None
            self.playwright = None
            return "Browser closed"
        except Exception as e:
            return f"Error closing browser: {str(e)}"

# Test usage
if __name__ == "__main__":
    browser = BrowserSkill()
    print(browser.start_browser())
    time.sleep(2)
    print(browser.open_website("youtube"))
    time.sleep(5)
    print(browser.close_browser())
```

### 1.3 Test New Browser Skill

```powershell
cd C:\coco
.\venv\Scripts\activate
python skills\browser_skill.py
```

Expected: Your default browser opens, goes to YouTube with YOUR profile (logged in!), waits 5 seconds, closes.

If this works → ✅ Browser skill fixed!

---

## STEP 2 — Fix Task Executor to Use Browser Skill Properly

### 2.1 Update Task Executor

Open `C:\coco\core\task_executor.py`

Find the `execute_skill` function and **REPLACE** the browser section:

```python
def execute_skill(self, intent, parameters):
    """Execute skill (copied from coco_refined.py for consistency)"""
    if not intent or intent == "null":
        return None
    
    try:
        skill_name, action_name = intent.split(".")
        
        if skill_name == "browser":
            if action_name == "open_website":
                url = parameters.get('url', '')
                result = self.skills.browser.open_website(url)
                return result
            elif action_name == "search_google":
                query = parameters.get('query', '')
                result = self.skills.browser.search_google(query)
                return result
            elif action_name == "close_browser":
                result = self.skills.browser.close_browser()
                return result
        
        elif skill_name == "system":
            if action_name == "open_app":
                app = parameters.get('app', '')
                result = self.skills.system.open_application(app)
                return result
            elif action_name == "close_app":
                app = parameters.get('app', '')
                result = self.skills.system.close_application(app)
                return result
        
        elif skill_name == "keyboard":
            if action_name == "type_text":
                text = parameters.get('text', '')
                result = self.skills.keyboard.type_text(text)
                return result
            elif action_name == "press_key":
                key = parameters.get('key', '')
                result = self.skills.keyboard.press_key(key)
                return result
            elif action_name == "screenshot":
                result = self.skills.keyboard.take_screenshot()
                return result
        
        elif skill_name == "files":
            if action_name == "create_file":
                filepath = parameters.get('filepath', 'new_file.txt')
                content = parameters.get('content', '')
                result = self.skills.files.create_file(filepath, content)
                return result
        
        return f"Executed {intent}"
    
    except Exception as e:
        return f"Error executing {intent}: {str(e)}"
```

---

## STEP 3 — Update LLM Prompt for Better URL Parsing

### 3.1 Update System Prompt

Open `C:\coco\core\coco_advanced.py`

Find `ADVANCED_SYSTEM_PROMPT` and update the browser examples:

```python
ADVANCED_SYSTEM_PROMPT = """You are coco, an advanced AI agent with multi-step execution, scheduling, and workflow capabilities.

You can now handle complex requests:
- Multi-step tasks: "Open notepad AND type hello AND save it"
- Scheduling: "Check weather every hour" or "Remind me at 3pm"
- Workflows: "Run my morning routine"
- Integrations: Weather, email (if configured)
- Browser control: "Open YouTube", "Search for AI news"

Response Format (JSON):
{
  "type": "single" | "multi_step" | "schedule" | "workflow" | "conversation",
  "intent": "skill.action" or null,
  "parameters": {},
  "steps": [],  // For multi-step tasks
  "schedule": {},  // For scheduled tasks
  "workflow_name": "",  // For workflow execution
  "response": "What to say to user"
}

Browser URL Rules:
- "open YouTube" → parameters: {"url": "youtube"}
- "open Google" → parameters: {"url": "google"}
- "open gmail.com" → parameters: {"url": "gmail.com"}
- "go to example.com" → parameters: {"url": "example.com"}
- Just use the site NAME, browser skill will handle full URL

Examples:

User: "Open YouTube"
{
  "type": "single",
  "intent": "browser.open_website",
  "parameters": {"url": "youtube"},
  "response": "Opening YouTube"
}

User: "Search Google for AI news"
{
  "type": "single",
  "intent": "browser.search_google",
  "parameters": {"query": "AI news"},
  "response": "Searching for AI news"
}

User: "Open Chrome and go to GitHub"
{
  "type": "multi_step",
  "steps": [
    {"intent": "browser.open_website", "parameters": {"url": "github"}, "description": "Open GitHub", "delay": 0}
  ],
  "response": "Opening GitHub in your browser"
}

User: "Open notepad"
{
  "type": "single",
  "intent": "system.open_app",
  "parameters": {"app": "notepad"},
  "response": "Opening notepad"
}

User: "Check weather every hour"
{
  "type": "schedule",
  "schedule": {"type": "interval", "minutes": 60},
  "intent": "integration.weather",
  "response": "I'll check the weather every hour"
}

User: "Run morning routine"
{
  "type": "workflow",
  "workflow_name": "morning_routine",
  "response": "Running your morning routine"
}

User: "What's the weather?"
{
  "type": "single",
  "intent": "integration.weather",
  "parameters": {},
  "response": "Let me check the weather"
}

Always respond with valid JSON."""
```

---

## STEP 4 — Add Browser Profile Detection Helper

Create `C:\coco\skills\test_browser_profile.py`:

```python
import os
import platform

def detect_browser_and_profile():
    """Detect browser and profile location"""
    system = platform.system()
    home = os.path.expanduser("~")
    
    print("="*60)
    print("  Browser Profile Detection")
    print("="*60)
    
    if system == "Windows":
        print("\nChecking for browser profiles...\n")
        
        # Chrome
        chrome_path = os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
        if os.path.exists(chrome_path):
            print(f"✅ Chrome profile found:")
            print(f"   {chrome_path}")
            
            # List profiles
            try:
                profiles = [d for d in os.listdir(chrome_path) if d.startswith("Profile") or d == "Default"]
                print(f"   Profiles: {', '.join(profiles)}")
            except:
                pass
        else:
            print("❌ Chrome profile not found")
        
        print()
        
        # Edge
        edge_path = os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data")
        if os.path.exists(edge_path):
            print(f"✅ Edge profile found:")
            print(f"   {edge_path}")
            
            try:
                profiles = [d for d in os.listdir(edge_path) if d.startswith("Profile") or d == "Default"]
                print(f"   Profiles: {', '.join(profiles)}")
            except:
                pass
        else:
            print("❌ Edge profile not found")
        
        print()
        
        # Check default browser
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice")
            prog_id = winreg.QueryValueEx(key, "ProgId")[0]
            winreg.CloseKey(key)
            
            print(f"Default browser: {prog_id}")
            
            if "Chrome" in prog_id:
                print("   → Will use Chrome")
            elif "Edge" in prog_id or "MSEdge" in prog_id:
                print("   → Will use Edge")
            else:
                print(f"   → Unknown browser type")
        except Exception as e:
            print(f"Could not detect default browser: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    detect_browser_and_profile()
```

Run:
```powershell
python skills\test_browser_profile.py
```

This shows which browser and profile coco will use.

---

## STEP 5 — Test Complete Flow

### 5.1 Test Browser Skill Directly

```powershell
python -c "from skills.browser_skill import BrowserSkill; b = BrowserSkill(); b.start_browser(); b.open_website('youtube'); import time; time.sleep(5); b.close_browser()"
```

Expected: Opens YOUR browser with YOUR profile, goes to YouTube (you should be logged in!), closes after 5 seconds.

### 5.2 Test via coco Agent

Start coco:
```powershell
python core\coco_advanced.py
```

Then type (since audio might not be set up yet):

**Test 1: Simple website**
```
Open YouTube
```

**Test 2: Search**
```
Search Google for Python tutorials
```

**Test 3: Multiple sites**
```
Open Gmail
```

All should open in YOUR browser with YOUR profile!

---

## STEP 6 — Create Quick Browser Test Script

Create `C:\coco\test_browser_now.py`:

```python
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
```

Run:
```powershell
python test_browser_now.py
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Opens Chromium instead of Chrome | Playwright default | Browser skill now detects and uses installed browser |
| Guest mode (not logged in) | No user profile | Browser skill now uses user data directory |
| "YouTube" doesn't work | URL parsing | Browser skill now has site mappings |
| Browser doesn't open at all | Playwright not finding browser | Run `playwright install` again |
| Profile path error | Wrong Windows username | Check path in test_browser_profile.py |
| Multiple browser windows | Not closing properly | Browser skill cleanup improved |

---

## Profile Locations Reference

**Chrome:**
```
C:\Users\{username}\AppData\Local\Google\Chrome\User Data
```

**Edge:**
```
C:\Users\{username}\AppData\Local\Microsoft\Edge\User Data
```

**Firefox:** (more complex - handled differently)
```
C:\Users\{username}\AppData\Roaming\Mozilla\Firefox\Profiles\
```

---

## Advanced: Use Specific Profile

If you have multiple Chrome profiles (Personal, Work, etc.):

In `browser_skill.py`, modify `launch_persistent_context`:

```python
# Use specific profile
profile_dir = os.path.join(self.user_data_dir, "Profile 1")  # or "Default"

self.browser = self.playwright.chromium.launch_persistent_context(
    user_data_dir=profile_dir,  # Specific profile
    headless=headless,
    args=launch_args['args'],
    channel="chrome"
)
```

---

## Verification Checklist

After completing Phase 3.5:

- [ ] Browser opens when you say "Open YouTube"
- [ ] Browser is YOUR default browser (Chrome/Edge/etc)
- [ ] You are LOGGED IN (your profile loads)
- [ ] "youtube" converts to "youtube.com" correctly
- [ ] Search functionality works
- [ ] Browser closes properly when done
- [ ] Works with text commands in coco

---

## Next Steps

Once browser is working:
1. Test all browser commands thoroughly
2. Add more site mappings to `normalize_url()` if needed
3. Move on to fixing audio/wake detection (if not done yet)
4. Test full voice → browser automation flow

---

🎉 **Browser Now Uses Real Profile!**

coco will now:
- Use YOUR default browser
- Load YOUR profile (passwords, bookmarks, history)
- Understand "open YouTube" without full URL
- Actually execute browser actions instead of just saying it will

Test it now with:
```powershell
python test_browser_now.py
```
