# NeuroLearn — start without activating venv (avoids execution policy issues)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "ERROR: venv not found. Create it first:" -ForegroundColor Red
    Write-Host "  python -m venv venv"
    Write-Host "  .\venv\Scripts\pip install -r requirements.txt"
    exit 1
}

# Dev-friendly defaults (override .env for this session)
$env:FLASK_DEBUG = "1"
if (-not $env:FLASK_SECRET_KEY) {
    $env:FLASK_SECRET_KEY = "dev-only-change-in-production"
}

Write-Host "Using: $python" -ForegroundColor Cyan
& $python run.py
