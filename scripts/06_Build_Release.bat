@echo off
setlocal
cd /d "%~dp0.." || exit /b 1
call "scripts\04_Build_Exe.bat" || exit /b 1
if defined NS_SIGN_THUMBPRINT (
  call "scripts\Sign_Exe.bat" || exit /b 1
)
call "scripts\05_Build_Installer.bat" || exit /b 1
if defined NS_SIGN_THUMBPRINT (
  call "scripts\Sign_Installer.bat" || exit /b 1
) else (
  echo No signing certificate configured. This is an UNSIGNED test build.
)
powershell.exe -NoProfile -Command "Get-FileHash -Algorithm SHA256 'installer\NorthStarWirelessSimulator_2.2.5_Setup.exe' | Format-List | Out-File -Encoding utf8 'installer\SHA256.txt'" || exit /b 1
echo Build complete. Clean-machine Windows QA is still required before release.
exit /b 0
