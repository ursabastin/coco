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
            print(f"[FOUND] Chrome profile found:")
            print(f"   {chrome_path}")
            
            # List profiles
            try:
                profiles = [d for d in os.listdir(chrome_path) if d.startswith("Profile") or d == "Default"]
                print(f"   Profiles: {', '.join(profiles)}")
            except:
                pass
        else:
            print("[MISSING] Chrome profile not found")
        
        print()
        
        # Edge
        edge_path = os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data")
        if os.path.exists(edge_path):
            print(f"[FOUND] Edge profile found:")
            print(f"   {edge_path}")
            
            try:
                profiles = [d for d in os.listdir(edge_path) if d.startswith("Profile") or d == "Default"]
                print(f"   Profiles: {', '.join(profiles)}")
            except:
                pass
        else:
            print("[MISSING] Edge profile not found")
        
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
