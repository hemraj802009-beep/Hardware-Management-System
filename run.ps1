# Hardware Store Management System - single command runner
# Usage: .\run.ps1   (or: powershell -ExecutionPolicy Bypass -File run.ps1)

$ErrorActionPreference = "Stop"

Write-Host "Installing dependencies (if any)..." -ForegroundColor Cyan
pip install -r requirements.txt | Out-Null

Write-Host "Starting FastAPI server (frontend + backend)..." -ForegroundColor Green
Write-Host "Open http://localhost:8000 in your browser" -ForegroundColor Yellow

python main.py