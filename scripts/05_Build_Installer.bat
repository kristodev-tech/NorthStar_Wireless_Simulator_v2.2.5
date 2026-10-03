@echo off
setlocal
cd /d "%~dp0.." || exit /b 1
if not exist "dist\NorthStarWirelessSimulator\NorthStarWirelessSimulator.exe" (
  echo Build the EXE first with 04_Build_Exe.bat.
  exit /b 1
)
call "scripts\Verify_Build.bat" || exit /b 1
if not defined ISCC set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo Inno Setup 6 compiler not found. Install it or set ISCC to its full path.
  exit /b 1
)
if exist "installer\NorthStarWirelessSimulator_2.2.5_Setup.exe" del /q "installer\NorthStarWirelessSimulator_2.2.5_Setup.exe" || exit /b 1
"%ISCC%" "packaging\NorthStarWirelessSimulator.iss" || exit /b 1
if not exist "installer\NorthStarWirelessSimulator_2.2.5_Setup.exe" exit /b 1
echo Installer built. See docs\Release_Checklist.md for Windows QA.
exit /b 0
