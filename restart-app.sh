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

# Kill any existing Flutter/backend processes
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
python3 run.py > /tmp/theheist-backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}   ✓ Backend starting (PID: $BACKEND_PID)${NC}"
echo -e "     Logs: tail -f /tmp/theheist-backend.log"
sleep 3
echo ""

# Check if backend is healthy
echo -e "${YELLOW}3. Checking backend health...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Backend is healthy${NC}"
else
    echo -e "${RED}   ✗ Backend failed to start!${NC}"
    echo -e "     Check logs: tail -f /tmp/theheist-backend.log"
    exit 1
fi
echo ""

# Clean Flutter build
echo -e "${YELLOW}4. Cleaning Flutter build...${NC}"
cd "$SCRIPT_DIR/app"
flutter clean > /dev/null 2>&1
echo -e "${GREEN}   ✓ Flutter cleaned${NC}"
echo ""

# Get Flutter packages
echo -e "${YELLOW}5. Getting Flutter packages...${NC}"
flutter pub get
echo -e "${GREEN}   ✓ Packages updated${NC}"
echo ""

# Start Flutter web app (single instance, multiple browser tabs)
echo -e "${YELLOW}6. Starting Flutter web app...${NC}"
echo -e "   Running on port 8087"
echo -e "   This may take 30-60 seconds..."
echo ""

# Start Flutter instance with web-server (doesn't auto-open browser)
flutter run -d web-server --web-hostname=localhost --web-port=8087 > /tmp/theheist-flutter.log 2>&1 &
FLUTTER_PID=$!
echo -e "${GREEN}   ✓ Flutter starting (PID: $FLUTTER_PID)${NC}"
echo ""

# Wait for Flutter to build and start
echo -e "${YELLOW}7. Waiting for Flutter to build...${NC}"
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
echo -e "  Logs:"
echo -e "    Backend:  tail -f /tmp/theheist-backend.log"
echo -e "    Flutter:  tail -f /tmp/theheist-flutter.log"
echo ""
echo -e "  To stop:"
echo -e "    pkill -f \"flutter run\""
echo -e "    pkill -f \"python.*run.py\""
echo ""
echo -e "${BLUE}======================================${NC}"
