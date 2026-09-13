@echo off
setlocal
cd /d "%~dp0"
echo Setting up PID Studio...
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m unittest discover
if errorlevel 1 goto failed
echo Setup complete. Double-click launch.cmd to open PID Studio.
exit /b 0
:failed
echo Setup failed. Review the message above.
pause
exit /b 1
