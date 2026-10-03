@echo off
setlocal
cd /d "%~dp0.." || exit /b 1
call "scripts\03_Quality_Checks.bat" || exit /b 1
if exist "dist\NorthStarWirelessSimulator" rmdir /s /q "dist\NorthStarWirelessSimulator" || exit /b 1
".venv\Scripts\python.exe" -m PyInstaller --clean --noconfirm "packaging\NorthStarWirelessSimulator.spec" || exit /b 1
if not exist "dist\NorthStarWirelessSimulator\NorthStarWirelessSimulator.exe" exit /b 1
call "scripts\Verify_Build.bat" || exit /b 1
echo Executable built and self-check passed. Test its visible UI before distributing.
exit /b 0
