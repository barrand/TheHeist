#!/bin/bash
# Quick start script for Image Playground

echo "🎨 Starting Image Playground..."
echo ""

# Check if venv exists, if not suggest creating one
if [ ! -d "venv" ]; then
    echo "💡 Tip: Create a virtual environment first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo ""
fi

# Start the app
python3 app.py
