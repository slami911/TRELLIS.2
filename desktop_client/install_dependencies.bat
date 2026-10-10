@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 or newer was not found. Install it from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)
py -3 -m pip install --upgrade pip
if errorlevel 1 goto :error
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :error
echo Dependencies installed successfully.
pause
exit /b 0
:error
echo Installation failed. Check the error above.
pause
exit /b 1
