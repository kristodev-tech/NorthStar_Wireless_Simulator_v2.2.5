@echo off
setlocal
cd /d "%~dp0.." || exit /b 1
if exist ".venv\Scripts\python.exe" goto install
if not "%~1"=="" (
  py -%~1 -m venv .venv || goto fail
  goto install
)
for %%V in (3.12 3.13 3.11) do (
  py -%%V -c "import sys; assert sys.version_info[:2] in [(3,11),(3,12),(3,13)]" >nul 2>nul
  if not errorlevel 1 (
    py -%%V -m venv .venv || goto fail
    goto install
  )
)
python -c "import sys; assert sys.version_info[:2] in [(3,11),(3,12),(3,13)]" >nul 2>nul || goto no_python
python -m venv .venv || goto fail
:install
".venv\Scripts\python.exe" -c "import sys; assert sys.version_info[:2] in [(3,11),(3,12),(3,13)]" || goto fail
".venv\Scripts\python.exe" -m pip install --upgrade pip || goto fail
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt || goto fail
".venv\Scripts\python.exe" -m pip check || goto fail
echo Environment ready. Run 02_Run_App.bat next.
exit /b 0
:no_python
echo Python 3.11, 3.12, or 3.13 is required. Install 64-bit Python with the Windows launcher.
exit /b 1
:fail
echo Setup failed. Review the error above. The build cannot continue.
exit /b 1
