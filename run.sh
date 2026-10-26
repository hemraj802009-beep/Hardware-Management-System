#!/usr/bin/env bash
set -e

echo "Installing dependencies (if any)..."
pip install -r requirements.txt >/dev/null

echo "Starting FastAPI server (frontend + backend)..."
echo "Open http://localhost:8000 in your browser"

python main.py