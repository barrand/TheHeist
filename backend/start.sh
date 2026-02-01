#!/bin/bash
# Start backend with clean environment

# Clear any existing GEMINI environment variables
unset GEMINI_API_KEY
unset GEMINI_MODEL

# Start the backend
cd "$(dirname "$0")"
python3 run.py
