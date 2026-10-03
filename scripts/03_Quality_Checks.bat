@echo off
setlocal
cd /d "%~dp0.." || exit /b 1
if not exist ".venv\Scripts\python.exe" (
  echo Run 01_Setup_Environment.bat first.
  exit /b 1
)
".venv\Scripts\python.exe" "scripts\quality_checks.py" %*
exit /b %errorlevel%
