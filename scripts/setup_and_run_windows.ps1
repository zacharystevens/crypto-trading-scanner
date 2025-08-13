Param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

# Move to repo root
$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

$venvPath = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path $venvPath)) {
  Write-Host "[setup] Creating virtual environment at $venvPath"
  & $Python -m venv $venvPath
}

# Activate venv
$activate = Join-Path $venvPath "Scripts\Activate.ps1"
. $activate

Write-Host "[setup] Upgrading pip"
python -m pip install --upgrade pip wheel setuptools

Write-Host "[setup] Installing requirements"
pip install -r requirements.txt

Write-Host "[run] Starting Flask dashboard on http://localhost:5001"
python flask_dashboard.py


