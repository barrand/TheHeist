#!/bin/bash
# Quick start script for Image Playground

echo "Starting Image Playground..."
echo ""

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python3 app.py
