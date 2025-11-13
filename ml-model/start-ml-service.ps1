# Start ML Service Script
Write-Host "Starting Flask ML Service..." -ForegroundColor Green

# Activate virtual environment
$venvPath = Join-Path $PSScriptRoot "..\venv\Scripts\Activate.ps1"
& $venvPath

# Start Flask app
python app.py
