#!/bin/bash
# Start backend with clean environment

# Clear any existing GEMINI environment variables
unset GEMINI_API_KEY
unset GEMINI_MODEL

# Start the backend
cd "$(dirname "$0")"

# Use venv if available, otherwise fall back to system python3
if [ -f "venv/bin/python3" ]; then
    venv/bin/python3 run.py
else
    python3 run.py
fi
