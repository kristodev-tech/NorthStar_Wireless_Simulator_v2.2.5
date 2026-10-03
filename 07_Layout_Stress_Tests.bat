@echo off
setlocal
cd /d "%~dp0" || exit /b 1
call "scripts\07_Layout_Stress_Tests.bat" %*
set "NS_RESULT=%errorlevel%"
if not "%NS_RESULT%"=="0" echo Optional stress checks reported issues. Review build\quality_checks_stress.log.
if not defined NS_AUTOMATED pause
exit /b %NS_RESULT%
