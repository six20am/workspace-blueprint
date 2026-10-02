@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup\setup.ps1" -Yes
if errorlevel 1 (
  echo.
  echo Setup stopped. The message above says why. Read setup\setup-report.md for the full list.
  pause
)
