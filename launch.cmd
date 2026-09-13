@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  call setup.cmd
  if errorlevel 1 exit /b 1
)
.venv\Scripts\python.exe run_studio.py %*
if errorlevel 1 pause
