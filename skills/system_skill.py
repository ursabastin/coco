import os
import subprocess
import time
import platform

class SystemSkill:
    def __init__(self):
        print("[SystemSkill] Initialized")
    
    def open_application(self, app_name):
        """Open ANY application installed on Windows using PowerShell search"""
        try:
            if platform.system() == "Windows":
                print(f"[SystemSkill] Searching for app: {app_name}...")
                
                # 1. First, try a simple startfile (works for notepad, calc, etc.)
                try:
                    os.startfile(app_name)
                    time.sleep(2)
                    return f"Opened {app_name}"
                except:
                    pass
                
                # 2. Use PowerShell to search the Start Menu / Apps Folder
                # This finds almost any installed app including Windows Store apps
                ps_command = f'Get-StartApps | Where-Object {{ $_.Name -like "*{app_name}*" }} | Select-Object -First 1 | ForEach-Object {{ Start-Process "shell:AppsFolder\\$($_.AppID)" }}'
                
                result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
                
                if result.returncode == 0:
                    time.sleep(2.5) # Focus delay
                    return f"Found and opened {app_name} via system search."
                else:
                    return f"Could not find an app named '{app_name}' on your system."
            else:
                return "System skill only supported on Windows for now"
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    
    def close_application(self, app_name):
        try:
            if platform.system() == "Windows":
                # Try killing by name
                subprocess.run(['taskkill', '/F', '/IM', f"{app_name}.exe"], capture_output=True)
                return f"Attempted to close {app_name}"
        except Exception as e:
            return f"Error closing {app_name}: {str(e)}"

    def list_running_apps(self):
        try:
            output = subprocess.check_output('tasklist', shell=True).decode()
            return output.splitlines()
        except:
            return []

    def set_volume(self, level):
        try:
            cmd = f"$obj = new-object -com wscript.shell;for($i=0;$i -lt 50;$i++){{$obj.sendkeys([char]174)}};for($i=0;$i -lt {int(level/2)};$i++){{$obj.sendkeys([char]175)}}"
            subprocess.run(["powershell", "-Command", cmd])
            return f"Volume set to {level}"
        except:
            return "Failed to set volume"
