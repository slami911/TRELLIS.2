@echo off
setlocal
cd /d "%~dp0"
py -3 app.py
if errorlevel 1 (
  echo The app could not start. Run install_dependencies.bat first.
  pause
)
