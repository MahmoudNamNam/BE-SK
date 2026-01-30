#!/usr/bin/env bash
# Create venv, install dependencies, and run the Skin Tone Classifier API (Mac/Linux)

set -e
cd "$(dirname "$0")"

VENV_DIR=".venv"

echo "Creating virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR"

echo "Activating virtual environment..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip --quiet

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

echo "Starting API (uvicorn main:app --host 0.0.0.0 --port 8000)..."
echo "Optional: set ROBOFLOW_API_KEY for eye detection (darkcircle/eyebag)."
export PYTHONPATH="${PWD}/src"
exec uvicorn main:app --host 0.0.0.0 --port 8000
