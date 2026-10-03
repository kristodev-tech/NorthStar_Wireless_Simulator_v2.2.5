@echo off
setlocal
cd /d "%~dp0.." || exit /b 1
if not defined SIGNTOOL set "SIGNTOOL=signtool.exe"
if not defined NS_SIGN_THUMBPRINT (
  echo Set NS_SIGN_THUMBPRINT to your code-signing certificate thumbprint.
  exit /b 1
)
if not exist "dist\NorthStarWirelessSimulator\NorthStarWirelessSimulator.exe" exit /b 1
if defined NS_TIMESTAMP_URL (
  "%SIGNTOOL%" sign /sha1 "%NS_SIGN_THUMBPRINT%" /fd SHA256 /tr "%NS_TIMESTAMP_URL%" /td SHA256 "dist\NorthStarWirelessSimulator\NorthStarWirelessSimulator.exe" || exit /b 1
) else (
  "%SIGNTOOL%" sign /sha1 "%NS_SIGN_THUMBPRINT%" /fd SHA256 "dist\NorthStarWirelessSimulator\NorthStarWirelessSimulator.exe" || exit /b 1
)
"%SIGNTOOL%" verify /pa /v "dist\NorthStarWirelessSimulator\NorthStarWirelessSimulator.exe" || exit /b 1
exit /b 0
