import time
import json
import threading
from datetime import datetime

class TaskExecutor:
    def __init__(self, skill_manager, memory_manager):
        self.skills = skill_manager
        self.memory = memory_manager
        self.current_task = None
        self.task_history = []
    
    def parse_multi_step_command(self, llm_response):
        """Check if LLM response contains multiple steps"""
        if isinstance(llm_response, dict) and 'steps' in llm_response:
            return llm_response['steps']
        return None
    
    def execute_step(self, step):
        """Execute a single step"""
        intent = step.get('intent')
        parameters = step.get('parameters', {})
        delay = step.get('delay', 0)
        
        if delay > 0:
            print(f"[TaskExecutor] Waiting {delay} seconds...")
            time.sleep(delay)
        
        # Execute via skill manager
        result = self.execute_skill(intent, parameters)
        
        # Log step
        step_log = {
            'timestamp': datetime.now().isoformat(),
            'intent': intent,
            'parameters': parameters,
            'result': result
        }
        self.task_history.append(step_log)
        return result
    
    def execute_skill(self, intent, parameters):
        """Execute skill action with tab support"""
        if not intent or intent == "null": return None
        
        try:
            skill_name, action_name = intent.split(".")
            
            if skill_name == "browser":
                tab_name = parameters.get('tab', 'default')
                if action_name == "open_website":
                    return self.skills.browser.open_website(parameters.get('url', ''), tab_name)
                elif action_name == "search":
                    return self.skills.browser.search_in_tab(parameters.get('query', ''), tab_name)
                elif action_name == "click":
                    return self.skills.browser.click_element(parameters.get('selector', ''), tab_name)
                elif action_name == "type":
                    return self.skills.browser.type_in_element(parameters.get('selector', ''), parameters.get('text', ''), tab_name)
                elif action_name == "close_browser":
                    return self.skills.browser.close_browser()
            
            elif skill_name == "system":
                if action_name == "open_app":
                    return self.skills.system.open_application(parameters.get('app', ''))
                elif action_name == "close_app":
                    return self.skills.system.close_application(parameters.get('app', ''))
            
            elif skill_name == "keyboard":
                if action_name == "type_text":
                    return self.skills.keyboard.type_text(parameters.get('text', ''))
                elif action_name == "press_key":
                    return self.skills.keyboard.press_key(parameters.get('key', ''))
                elif action_name == "screenshot":
                    return self.skills.keyboard.take_screenshot()
            
            elif skill_name == "files":
                if action_name == "create_file":
                    return self.skills.files.create_file(parameters.get('filepath', 'file.txt'), parameters.get('content', ''))
            
            return f"Executed {intent}"
        except Exception as e:
            return f"Error executing {intent}: {str(e)}"
    
    def execute_multi_step_task(self, steps):
        """Execute multiple steps, allowing for parallel execution"""
        results = []
        print(f"[TaskExecutor] Starting multi-step task with {len(steps)} steps")
        
        parallel_steps = [s for s in steps if s.get('parallel') == True]
        sequential_steps = [s for s in steps if not s.get('parallel')]
        
        # Execute parallel steps in threads
        threads = []
        def run_parallel(s, idx):
            res = self.execute_step(s)
            results.append({'step': f"P{idx}", 'description': s.get('description', ''), 'result': res})

        for i, step in enumerate(parallel_steps):
            print(f"[TaskExecutor] Launching Parallel Step P{i+1}: {step.get('description')}")
            t = threading.Thread(target=run_parallel, args=(step, i+1))
            t.start()
            threads.append(t)
        
        # Execute sequential steps
        for i, step in enumerate(sequential_steps, 1):
            print(f"[TaskExecutor] Sequential Step {i}/{len(sequential_steps)}: {step.get('description')}")
            result = self.execute_step(step)
            
            is_success = not ("error" in str(result).lower() or "fail" in str(result).lower())
            
            results.append({
                'step': f"S{i}", 
                'description': step.get('description', ''), 
                'result': result,
                'success': is_success
            })
            
            if not is_success:
                print(f"[TaskExecutor] Stopping due to error: {result}")
                break
        
        # Wait for parallel threads to finish
        for t in threads:
            t.join()
            
        return results
    
    def get_task_summary(self, results):
        total = len(results)
        success = sum(1 for r in results if not ("error" in str(r['result']).lower()))
        return f"Completed {success}/{total} steps successfully."

if __name__ == "__main__":
    # Internal test logic simplified for length
    pass
