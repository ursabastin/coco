# coco — Phase 1: Solving Whisper Module Error
### Troubleshooting Guide

---

## The Error You're Seeing

```
[Running] python -u "c:\Users\ursab\coco\core\coco_core.py"
Traceback (most recent call last):
  File "c:\Users\ursab\coco\core\coco_core.py", line 2, in <module>
    import whisper
ModuleNotFoundError: No module named 'whisper'
```

---

## What This Means

The Python script is trying to import `whisper`, but it can't find it. This happens because:

**The virtual environment (venv) is NOT active when you're running the script.**

Python is looking in the wrong place for installed packages.

---

## SOLUTION 1: Activate Venv BEFORE Running (Recommended)

### Step 1: Open PowerShell Terminal in Antigravity
Press `Ctrl + ~` to open the terminal in Antigravity.

### Step 2: Navigate to coco Folder
```powershell
cd C:\coco
```

### Step 3: Activate the Virtual Environment
```powershell
.\venv\Scripts\activate
```

You should see `(venv)` appear at the start of your terminal line:
```
(venv) PS C:\coco>
```

### Step 4: Verify Whisper is Installed
```powershell
pip list | findstr whisper
```

Expected output:
```
openai-whisper    <version>
```

If you DON'T see it, install it:
```powershell
pip install openai-whisper
```

### Step 5: Run the Script
```powershell
python core\coco_core.py
```

---

## SOLUTION 2: Configure VS Code/Antigravity to Use Venv Automatically

### Step 1: Select Python Interpreter
1. In Antigravity, press `Ctrl + Shift + P`
2. Type: `Python: Select Interpreter`
3. Choose: `.\venv\Scripts\python.exe` (it should show `Python 3.11.x ('venv': venv)`)

### Step 2: Verify Selection
Look at the bottom-right corner of Antigravity. It should show:
```
Python 3.11.x ('venv': venv)
```

### Step 3: Restart Terminal
Close and reopen the terminal (`Ctrl + ~`). The `(venv)` should appear automatically.

### Step 4: Run the Script
```powershell
python core\coco_core.py
```

---

## SOLUTION 3: Install Packages in the Correct Environment

If whisper still isn't found, reinstall all packages:

### Step 1: Activate Venv
```powershell
cd C:\coco
.\venv\Scripts\activate
```

### Step 2: Install All Requirements
```powershell
pip install -r requirements.txt
```

### Step 3: Verify Installation
```powershell
pip list
```

You should see:
- openai-whisper
- sounddevice
- scipy
- numpy
- requests
- kokoro-onnx
- soundfile
- pyaudio
- python-dotenv

---

## SOLUTION 4: Full Clean Reinstall (If Nothing Else Works)

### Step 1: Delete Old Venv
```powershell
cd C:\coco
Remove-Item -Recurse -Force venv
```

### Step 2: Create Fresh Venv
```powershell
python -m venv venv
```

### Step 3: Activate New Venv
```powershell
.\venv\Scripts\activate
```

### Step 4: Install Everything Fresh
```powershell
pip install --upgrade pip
pip install openai-whisper sounddevice scipy numpy requests kokoro-onnx soundfile pyaudio python-dotenv huggingface_hub
```

If `pyaudio` fails:
```powershell
pip install pipwin
pipwin install pyaudio
```

### Step 5: Download Whisper Model
```powershell
python -c "import whisper; whisper.load_model('medium')"
```

### Step 6: Run the Script
```powershell
python core\coco_core.py
```

---

## Quick Verification Checklist

Before running `coco_core.py`, verify these three things:

### ✅ Check 1: Is Venv Active?
Your terminal should show:
```
(venv) PS C:\coco>
```

### ✅ Check 2: Is Whisper Installed in Venv?
Run:
```powershell
pip show openai-whisper
```

Expected: Shows package details (name, version, location)

### ✅ Check 3: Is Python Using the Right Interpreter?
Run:
```powershell
python -c "import sys; print(sys.executable)"
```

Expected output should include `venv`:
```
C:\coco\venv\Scripts\python.exe
```

If all three checks pass → ✅ You're ready to run coco!

---

## How to Always Run coco Correctly

### Method 1: Use PowerShell Script (Easiest)

Create `C:\coco\run_coco.ps1`:

```powershell
cd C:\coco
.\venv\Scripts\activate
python core\coco_core.py
```

Then just double-click this file or run:
```powershell
.\run_coco.ps1
```

### Method 2: Use Batch File (Alternative)

Create `C:\coco\run_coco.bat`:

```batch
@echo off
cd C:\coco
call venv\Scripts\activate
python core\coco_core.py
pause
```

Then just double-click `run_coco.bat`.

---

## Common Mistakes to Avoid

❌ **Running from File Explorer** → Python won't find venv  
✅ **Run from terminal with venv active**

❌ **Installing with global Python** → Packages go to wrong place  
✅ **Always activate venv first, then install**

❌ **Using system Python** → Points to wrong interpreter  
✅ **Select venv interpreter in Antigravity**

❌ **Forgetting to activate venv** → Most common mistake!  
✅ **Always check for `(venv)` in terminal**

---

## Still Not Working?

If you've tried everything and it's still broken, run this diagnostic:

```powershell
cd C:\coco
.\venv\Scripts\activate
python -c "import sys; print('Python:', sys.executable); import whisper; print('Whisper found:', whisper.__version__)"
```

**If this works** → The issue is how you're running the script  
**If this fails** → Whisper isn't properly installed in venv

Copy the output and check which error appears.

---

## Pro Tip: Always Start This Way

Every time you want to run coco:

1. Open PowerShell or Antigravity terminal
2. `cd C:\coco`
3. `.\venv\Scripts\activate`
4. Verify you see `(venv)` in the prompt
5. `python core\coco_core.py`

Make this your routine. It takes 5 seconds and prevents 99% of issues.
