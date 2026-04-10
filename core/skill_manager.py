import sys
sys.path.append('c:/Users/ursab/coco')

from skills.browser_skill import BrowserSkill
from skills.system_skill import SystemSkill
from skills.keyboard_skill import KeyboardSkill
from skills.screen_skill import ScreenSkill
from skills.file_skill import FileSkill

class SkillManager:
    def __init__(self, network_monitor=None, voice_confirmer=None):
        print("[SkillManager] Initializing skills...")
        
        # Pass network support to browser skill
        self.browser = BrowserSkill(
            network_monitor=network_monitor,
            voice_confirmer=voice_confirmer
        )
        
        self.system = SystemSkill()
        self.keyboard = KeyboardSkill()
        self.screen = ScreenSkill()  # This takes ~30 seconds to load OCR
        self.files = FileSkill()
        print("[SkillManager] All skills loaded")
    
    def execute_command(self, intent, parameters):
        """Execute a command based on intent"""
        
        # Browser commands
        if intent == "open_website":
            return self.browser.open_website(parameters.get('url'))
        elif intent == "search_google":
            return self.browser.search_google(parameters.get('query'))
        elif intent == "close_browser":
            return self.browser.close_browser()
        
        # System commands
        elif intent == "open_app":
            return self.system.open_application(parameters.get('app'))
        elif intent == "close_app":
            return self.system.close_application(parameters.get('app'))
        elif intent == "list_apps":
            apps = self.system.list_running_apps()
            return f"Running: {', '.join(apps[:10])}"
        
        # Keyboard commands
        elif intent == "type_text":
            return self.keyboard.type_text(parameters.get('text'))
        elif intent == "press_key":
            return self.keyboard.press_key(parameters.get('key'))
        elif intent == "screenshot":
            return self.keyboard.take_screenshot(parameters.get('filename', 'screenshot.png'))
        
        # Screen reading
        elif intent == "read_screen":
            return self.screen.read_screen()
        
        # File operations
        elif intent == "create_file":
            return self.files.create_file(parameters.get('filepath'), parameters.get('content', ''))
        elif intent == "read_file":
            return self.files.read_file(parameters.get('filepath'))
        elif intent == "list_files":
            return str(self.files.list_files(parameters.get('folder', '.')))
        

        
        else:
            return f"Unknown intent: {intent}"
    
    def parse_natural_command(self, command):
        """Parse natural language command into intent and parameters"""
        command_lower = command.lower()
        
        # Browser patterns
        if "open" in command_lower and any(x in command_lower for x in ["website", "site", ".com", "http"]):
            # Extract URL
            words = command.split()
            url = next((w for w in words if '.com' in w or 'http' in w), None)
            if url:
                return ("open_website", {"url": url})
        
        elif "search" in command_lower and "google" in command_lower:
            # Extract query after "search" or "for"
            if "for" in command_lower:
                query = command_lower.split("for", 1)[1].strip()
            else:
                query = command_lower.replace("search", "").replace("google", "").strip()
            return ("search_google", {"query": query})
        
        elif "close browser" in command_lower:
            return ("close_browser", {})
        
        # System patterns
        elif "open" in command_lower and any(x in command_lower for x in ["notepad", "calculator", "paint", "chrome", "edge"]):
            app = next((x for x in ["notepad", "calculator", "paint", "chrome", "edge"] if x in command_lower), None)
            return ("open_app", {"app": app})
        
        elif "close" in command_lower:
            words = command_lower.split()
            app = words[-1] if words else ""
            return ("close_app", {"app": app})
        
        elif "what" in command_lower and "running" in command_lower:
            return ("list_apps", {})
        
        # Keyboard patterns
        elif "type" in command_lower:
            text = command.replace("type", "", 1).strip()
            return ("type_text", {"text": text})
        
        elif "screenshot" in command_lower:
            return ("screenshot", {})
        
        # Screen reading
        elif "read screen" in command_lower or "what's on screen" in command_lower:
            return ("read_screen", {})
        
        # File patterns
        elif "create file" in command_lower:
            return ("create_file", {"filepath": "created_file.txt", "content": "Created by coco"})
        
        elif "list files" in command_lower:
            return ("list_files", {"folder": "."})
        
        return (None, {})

# Test usage
if __name__ == "__main__":
    manager = SkillManager()
    
    test_commands = [
        "open google.com",
        "search google for AI automation",
        "open notepad",
        "type hello world",
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        intent, params = manager.parse_natural_command(cmd)
        if intent:
            result = manager.execute_command(intent, params)
            print(f"Result: {result}")
        else:
            print("Could not parse command")
