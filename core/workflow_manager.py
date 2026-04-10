import json
import os
from datetime import datetime

class WorkflowManager:
    def __init__(self, workflow_dir="data/workflows"):
        self.workflow_dir = workflow_dir
        os.makedirs(workflow_dir, exist_ok=True)
        self.workflows = {}
        self.load_all_workflows()
        print(f"[WorkflowManager] Loaded {len(self.workflows)} workflows")
    
    def create_workflow(self, name, description, steps):
        """Create and save a new workflow"""
        workflow = {
            'name': name,
            'description': description,
            'steps': steps,
            'created_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # Save to file
        filepath = os.path.join(self.workflow_dir, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        # Add to memory
        self.workflows[name] = workflow
        
        return f"Created workflow '{name}' with {len(steps)} steps"
    
    def load_workflow(self, name):
        """Load a workflow by name"""
        if name in self.workflows:
            return self.workflows[name]
        
        # Try loading from file
        filepath = os.path.join(self.workflow_dir, f"{name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                workflow = json.load(f)
                self.workflows[name] = workflow
                return workflow
        
        return None
    
    def load_all_workflows(self):
        """Load all workflows from directory"""
        if not os.path.exists(self.workflow_dir):
            return
        
        for filename in os.listdir(self.workflow_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.workflow_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        workflow = json.load(f)
                        self.workflows[workflow['name']] = workflow
                except Exception as e:
                    print(f"Error loading workflow {filename}: {e}")
    
    def list_workflows(self):
        """List all available workflows"""
        return list(self.workflows.keys())
    
    def get_workflow_details(self, name):
        """Get detailed info about a workflow"""
        workflow = self.load_workflow(name)
        if workflow:
            return {
                'name': workflow['name'],
                'description': workflow['description'],
                'steps': len(workflow['steps']),
                'created': workflow.get('created_at', 'Unknown')
            }
        return None
    
    def delete_workflow(self, name):
        """Delete a workflow"""
        # Remove from memory
        if name in self.workflows:
            del self.workflows[name]
        
        # Remove file
        filepath = os.path.join(self.workflow_dir, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return f"Deleted workflow '{name}'"
        
        return f"Workflow '{name}' not found"
    
    def export_workflow(self, name, export_path):
        """Export workflow to a file"""
        workflow = self.load_workflow(name)
        if workflow:
            with open(export_path, 'w') as f:
                json.dump(workflow, f, indent=2)
            return f"Exported '{name}' to {export_path}"
        return f"Workflow '{name}' not found"
    
    def import_workflow(self, import_path):
        """Import workflow from a file"""
        with open(import_path, 'r') as f:
            workflow = json.load(f)
            name = workflow['name']
            self.workflows[name] = workflow
            
            # Save to workflow directory
            filepath = os.path.join(self.workflow_dir, f"{name}.json")
            with open(filepath, 'w') as out:
                json.dump(workflow, out, indent=2)
            
            return f"Imported workflow '{name}'"

# Create default workflows
def create_default_workflows():
    """Create some example workflows"""
    manager = WorkflowManager()
    
    # Morning routine workflow
    manager.create_workflow(
        name="morning_routine",
        description="Open essential apps for the day",
        steps=[
            {
                'intent': 'browser.open_website',
                'parameters': {'url': 'gmail.com'},
                'description': 'Open email',
                'delay': 0
            },
            {
                'intent': 'browser.open_website',
                'parameters': {'url': 'calendar.google.com'},
                'description': 'Open calendar',
                'delay': 2
            },
            {
                'intent': 'system.open_app',
                'parameters': {'app': 'notepad'},
                'description': 'Open notepad for notes',
                'delay': 1
            }
        ]
    )
    
    # Screenshot and save workflow
    manager.create_workflow(
        name="screenshot_and_save",
        description="Take screenshot and save to specific location",
        steps=[
            {
                'intent': 'keyboard.screenshot',
                'parameters': {'filename': 'screenshot.png'},
                'description': 'Take screenshot',
                'delay': 0
            },
            {
                'intent': 'files.create_file',
                'parameters': {
                    'filepath': 'screenshots/notes.txt',
                    'content': f'Screenshot taken at {datetime.now()}'
                },
                'description': 'Log screenshot',
                'delay': 1
            }
        ]
    )
    
    print("[OK] Created default workflows")

# Test script
if __name__ == "__main__":
    create_default_workflows()
    
    manager = WorkflowManager()
    
    print("\nAvailable workflows:")
    for name in manager.list_workflows():
        details = manager.get_workflow_details(name)
        print(f"  - {name}: {details['description']} ({details['steps']} steps)")
