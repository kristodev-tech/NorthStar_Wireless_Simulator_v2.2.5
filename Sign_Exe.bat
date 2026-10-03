@echo off
setlocal
cd /d "%~dp0" || exit /b 1
call "scripts\Sign_Exe.bat" %*
set "NS_RESULT=%errorlevel%"
if not "%NS_RESULT%"=="0" echo Operation failed with code %NS_RESULT%.
if not defined NS_AUTOMATED pause
exit /b %NS_RESULT%
