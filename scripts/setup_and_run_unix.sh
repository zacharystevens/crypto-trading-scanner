#!/usr/bin/env bash
set -euo pipefail

# Cross-platform setup for macOS/Linux
# - Creates isolated venv
# - Installs requirements
# - Starts Flask dashboard

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] Creating virtual environment at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "[setup] Upgrading pip"
python -m pip install --upgrade pip wheel setuptools

echo "[setup] Installing requirements"
pip install -r requirements.txt

echo "[run] Starting Flask dashboard on http://localhost:5001"
echo "[info] First run will ask to configure API or use demo mode"
echo "[tip] Available flags:"
echo "      --demo (force demo mode)"
echo "      --api-binance (force Binance API)"
echo "      --api-bitunix (force Bitunix API)"
echo "      --config (reconfigure)"
exec python flask_dashboard.py


