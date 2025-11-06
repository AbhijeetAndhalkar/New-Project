# run.ps1 — Auto-activate virtual environment and run Flask app

# Ensure the script runs from its current folder
Set-Location $PSScriptRoot

Write-Host "Activating virtual environment..."
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

Write-Host "Setting FLASK_APP variable..."
$env:FLASK_APP = "app.py"

Write-Host "Starting Flask app..."
flask run
