@echo off
cd /d "%~dp0"
if not exist "%~dp0setup\setup.ps1" (
  echo.
  echo This file is still inside the zip. Right-click the zip, choose Extract All, open the new folder, then double-click setup.cmd there.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup\setup.ps1" -Yes
if errorlevel 1 (
  echo.
  echo Setup finished with problems. The message above says what to do. The full list is in setup\setup-report.md.
  pause
)
