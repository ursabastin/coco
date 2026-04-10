from core.skill_manager import SkillManager
from core.task_executor import TaskExecutor
import time

print("Testing Parallel Browser Multitasking...")

# Mock managers
class MockMemory:
    def add_interaction(self, *args, **kwargs): pass

# Real skills (this will actually open your browser!)
skills = SkillManager()
executor = TaskExecutor(skills, MockMemory())

# Simultaneous steps
steps = [
    {
        "intent": "browser.open_website",
        "parameters": {"url": "youtube", "tab": "youtube_test"},
        "parallel": True,
        "description": "Opening YouTube in background"
    },
    {
        "intent": "browser.open_website",
        "parameters": {"url": "gemini", "tab": "gemini_test"},
        "parallel": True,
        "description": "Opening Gemini in background"
    }
]

print("\nStarting parallel steps...")
start = time.time()
results = executor.execute_multi_step_task(steps)
end = time.time()

print(f"\nCompleted in {end - start:.2f} seconds.")
print("You should see TWO tabs open in your browser now.")

time.sleep(10)
skills.browser.close_browser()
