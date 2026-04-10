@echo off
cd /d "%~dp0\.."
echo [coco] Starting v0.0.3...
call venv\Scripts\activate
python main.py
pause
