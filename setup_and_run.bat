@echo off
REM Create venv, install dependencies, and run the Skin Tone Classifier API (Windows)
setlocal
cd /d "%~dp0"

set VENV_DIR=.venv

echo Creating virtual environment in %VENV_DIR%...
python -m venv "%VENV_DIR%"
if errorlevel 1 (
  echo Failed to create venv. Try: py -m venv "%VENV_DIR%" or install Python from python.org
  exit /b 1
)

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

echo Upgrading pip...
python -m pip install --upgrade pip -q

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt -q

echo Starting API (uvicorn main:app --host 0.0.0.0 --port 8000)...
echo Optional: set ROBOFLOW_API_KEY for eye detection (darkcircle/eyebag).
set "PYTHONPATH=%CD%\src"
uvicorn main:app --host 0.0.0.0 --port 8000

endlocal
