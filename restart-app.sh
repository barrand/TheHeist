#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  The Heist - Rebuild & Restart App${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Kill any existing Flutter/backend/E2E portal processes
echo -e "${YELLOW}1. Stopping existing processes...${NC}"
pkill -9 -f "flutter run" 2>/dev/null
pkill -9 -f "python.*run.py" 2>/dev/null
pkill -9 -f "flutter_tools_chrome_device" 2>/dev/null
lsof -ti:8087 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 3
echo -e "${GREEN}   ✓ Processes stopped${NC}"
echo ""

# Start backend server
echo -e "${YELLOW}2. Starting backend server...${NC}"
cd "$SCRIPT_DIR/backend"
mkdir -p /tmp/heist_logs
# Use venv (Python 3.12) if available, otherwise fall back to system python3
PYTHON="${SCRIPT_DIR}/backend/venv/bin/python3"
[ -f "$PYTHON" ] || PYTHON="python3"
$PYTHON run.py > /tmp/heist_logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}   ✓ Backend starting (PID: $BACKEND_PID)${NC}"
echo -e "     Logs: tail -f /tmp/heist_logs/backend.log"
sleep 3
echo ""

# Check if backend is healthy
echo -e "${YELLOW}3. Checking backend health...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Backend is healthy${NC}"
else
    echo -e "${RED}   ✗ Backend failed to start!${NC}"
    echo -e "     Check logs: tail -f /tmp/heist_logs/backend.log"
    exit 1
fi
echo ""

# Get Flutter packages (skip clean — incremental builds are ~10x faster)
# Pass --clean flag to force a full rebuild when needed: ./restart-app.sh --clean
echo -e "${YELLOW}4. Updating Flutter packages...${NC}"
cd "$SCRIPT_DIR/frontend"
if [[ "$*" == *"--clean"* ]]; then
    echo -e "   Running flutter clean (--clean flag passed)..."
    flutter clean > /dev/null 2>&1
    echo -e "${GREEN}   ✓ Flutter cleaned${NC}"
fi
flutter pub get > /dev/null 2>&1
echo -e "${GREEN}   ✓ Packages ready${NC}"
echo ""

# Start Flutter web app (single instance, multiple browser tabs)
echo -e "${YELLOW}7. Starting Flutter web app...${NC}"
echo -e "   Running on port 8087"
echo -e "   Incremental build — usually ready in 10-20s (first run after --clean may take longer)"
echo ""

# Start Flutter instance with web-server (doesn't auto-open browser)
cd "$SCRIPT_DIR/frontend"
flutter run -d web-server --web-hostname=localhost --web-port=8087 > /tmp/theheist-flutter.log 2>&1 &
FLUTTER_PID=$!
echo -e "${GREEN}   ✓ Flutter starting (PID: $FLUTTER_PID)${NC}"
echo ""

# Wait for Flutter to build and start
echo -e "${YELLOW}8. Waiting for Flutter to build...${NC}"
for i in {1..60}; do
    if lsof -i:8087 > /dev/null 2>&1; then
        echo -e "${GREEN}   ✓ Flutter web app is running!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""
echo ""

# Summary
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✓ The Heist is running!${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "  📱 Frontend:  ${GREEN}http://localhost:8087${NC}"
echo -e "  🔧 Backend:   ${GREEN}http://localhost:8000${NC}"
echo ""
echo -e "  ${YELLOW}Quick Test:${NC}"
echo -e "    1. Browser 1: Click 🎭 Test as Mastermind"
echo -e "    2. Browser 2: Click 🔐 Test as Safe Cracker → Enter room code"
echo -e "    3. Host clicks Start Game"
echo ""
echo -e "  Ctrl+C to stop tailing (app keeps running)"
echo ""
echo -e "${BLUE}======================================${NC}"
echo ""

tail -f /tmp/heist_logs/backend.log /tmp/theheist-flutter.log
