@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call setup.cmd
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install "pyinstaller==6.22.2"
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m unittest discover
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m PyInstaller --noconfirm PIDStudio.spec
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe verify_build.py
if errorlevel 1 exit /b 1
echo Portable application: dist\PIDStudio\PIDStudio.exe
echo Keep the entire PIDStudio folder together, including _internal.
