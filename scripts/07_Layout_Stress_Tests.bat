@echo off
setlocal
cd /d "%~dp0.." || exit /b 1
echo Optional developer layout stress tests. Not required for a normal EXE build.
call "scripts\03_Quality_Checks.bat" --layout-stress
exit /b %errorlevel%
