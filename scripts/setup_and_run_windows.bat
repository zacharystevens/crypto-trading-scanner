@echo off
setlocal enabledelayedexpansion

REM Move to repo root
pushd %~dp0\..

set VENV_DIR=.venv

where python >nul 2>nul
if errorlevel 1 (
  echo [error] Python not found in PATH
  echo Install Python 3 and ensure "Add Python to PATH" was selected.
  pause
  exit /b 1
)

if not exist %VENV_DIR% (
  echo [setup] Creating virtual environment at %VENV_DIR%
  python -m venv %VENV_DIR%
)

call %VENV_DIR%\Scripts\activate.bat

echo [setup] Upgrading pip
python -m pip install --upgrade pip wheel setuptools

echo [setup] Installing requirements
pip install -r requirements.txt

echo [run] Starting Flask dashboard on http://localhost:5001
python flask_dashboard.py

popd
endlocal


