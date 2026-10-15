@echo off
setlocal
title TermsLens AI
cd /d "%~dp0"
echo ============================================
echo             TermsLens AI
echo ============================================
if not exist ".venv\Scripts\python.exe" (
  echo Creating environment with the Windows py launcher...
  py -m venv .venv
  if errorlevel 1 goto error
)
if not exist ".venv\termslens_requirements_installed.txt" (
  echo Installing dependencies for the first run. Please wait...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 goto error
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto error
  echo installed>".venv\termslens_requirements_installed.txt"
)
echo Starting TermsLens AI...
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto error
goto end
:error
echo.
echo Startup failed. Read the error above.
pause
:end
endlocal
