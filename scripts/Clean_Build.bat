@echo off
setlocal
cd /d "%~dp0.." || exit /b 1
for %%D in (build dist installer) do (
  if exist "%%D" rmdir /s /q "%%D" || exit /b 1
)
echo Build outputs removed. Source, examples, and per-user data were preserved.
exit /b 0
