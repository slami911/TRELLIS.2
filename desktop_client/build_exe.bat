@echo off
setlocal
cd /d "%~dp0"
py -3 -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --collect-data gradio_client --collect-data safehttpx --name TRELLIS2-Desktop app.py
if errorlevel 1 goto :error
echo EXE created in: %CD%\dist\TRELLIS2-Desktop.exe
pause
exit /b 0
:error
echo Build failed. Check the error above.
pause
exit /b 1
