@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed yet. Run setup.cmd first.
  pause
  exit /b 1
)
python "%~dp0tools\update\update.py"
echo.
pause
