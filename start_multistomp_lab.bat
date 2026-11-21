@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m multistomp_lab.desktop
) else (
  python -m multistomp_lab.desktop
)
if errorlevel 1 (
  echo.
  echo Failed to start. Install Python 3.10+ with Tkinter enabled.
  pause
)
