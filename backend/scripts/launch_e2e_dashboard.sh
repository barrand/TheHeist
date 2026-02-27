#!/bin/bash

# E2E Testing Dashboard Launcher
# Starts backend server (if not running) and launches the E2E testing UI

echo ""
echo "======================================================================"
echo "🎮 Launching E2E Testing Dashboard"
echo "======================================================================"
echo ""

cd "$(dirname "$0")/.."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend not running. Starting backend server..."
    echo ""
    
    # Start backend in background
    ./start.sh &
    BACKEND_PID=$!
    
    echo "   Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "   ✅ Backend ready!"
            break
        fi
        sleep 1
    done
else
    echo "✅ Backend already running at http://localhost:8000"
fi

echo ""
echo "🚀 Starting E2E Testing Dashboard..."
# Use E2E_PORT if set; otherwise try 5556 if 5555 is busy
if [ -n "$E2E_PORT" ]; then
    echo "   Using port $E2E_PORT (from E2E_PORT)"
else
    if lsof -i :5555 > /dev/null 2>&1; then
        export E2E_PORT=5556
        echo "   Port 5555 in use, using 5556 instead"
    else
        echo "   Opening at: http://localhost:5555"
    fi
fi
echo ""
echo "======================================================================"
echo ""

# Launch UI server (pass port via env so Python inherits it)
E2E_PORT="${E2E_PORT:-5555}" python3 scripts/e2e_testing/ui_server.py
