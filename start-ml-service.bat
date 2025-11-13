@echo off
cd /d "%~dp0\ml-model"
call ..\venv\Scripts\activate.bat
python app.py
pause
