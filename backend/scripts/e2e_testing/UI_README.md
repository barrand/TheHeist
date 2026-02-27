# 🎮 E2E Testing Dashboard

A web-based UI for managing procedural scenario generation and automated E2E testing.

## Features

### 📋 Scenario Management
- **View all generated scenarios** with details (player count, tasks, roles)
- **Run E2E tests** on any scenario with one click
- **Generate new scenarios** with custom role selection

### 📊 Real-Time Monitoring
- **Backend log viewer** - See what the game server is doing
- **E2E test log viewer** - Watch bot players in action
- **Auto-scrolling logs** with color-coded severity levels
- **Process management** - Stop running tests anytime

### ✨ Scenario Generation
- Choose from predefined scenario types (museum, bank, office, casino, art gallery)
- Select 2-7 player roles from available options
- Optional seed for reproducible generation
- Instant validation and export to JSON + Markdown

## Quick Start

```bash
# 1. Install dependencies
cd backend/scripts/e2e_testing
pip3 install -r requirements.txt

# 2. Make sure backend server is running
cd ../../
./start.sh

# 3. Launch E2E Testing Dashboard
python3 scripts/e2e_testing/ui_server.py
```

The dashboard will automatically open at **http://localhost:5555**

## Usage

### Running E2E Tests
1. Click **▶ Run E2E Test** next to any scenario
2. Watch real-time logs in the bottom panels
3. Test runs automatically with bot players
4. Results show WIN/ERROR/DEADLOCK status

### Generating Scenarios
1. Click **✨ Generate New Scenario**
2. Select scenario type (museum_heist, bank_vault, etc.)
3. Check the roles you want (2-7 players)
4. Optional: Set a random seed for reproducibility
5. Click **Generate** - validation happens automatically
6. New scenario appears in the list

### Monitoring Logs
- **Backend Log** (left): Game server events, task completions, WebSocket messages
- **E2E Test Log** (right): Bot decisions, actions, test progress
- Both auto-scroll and color-code by severity
- Click **Clear** to reset a log viewer

### Stopping Tests
- Click **⏹ Stop Test** to kill a running E2E test
- Process and all children are terminated gracefully

## Architecture

```
ui_server.py (Flask)
├── /api/scenarios - List generated scenarios
├── /api/generate - Generate new scenario
├── /api/test/start - Start E2E test
├── /api/test/stop - Kill running test
├── /api/test/status - Check test status
├── /api/logs/backend/stream - Stream backend log (SSE)
└── /api/logs/e2e/stream - Stream E2E test log (SSE)

templates/index.html
├── Scenario list UI
├── Generation modal
└── Dual log viewers
```

## Tips

- **Keep backend running**: The dashboard works best when the backend server is already running
- **Log locations**: 
  - Backend: `/tmp/heist_logs/backend.log`
  - E2E: `/tmp/heist_logs/e2e_test.log`
- **Browser compatibility**: Works in Chrome, Firefox, Safari (requires Server-Sent Events support)

## Next Steps

Want to make this a proper macOS app? Wrap it with:
- **PyWebView** (Python → native macOS window)
- **Electron** (full featured, but larger)
- **Tauri** (Rust-based, lightweight)

For now, the web UI provides all functionality with minimal overhead!
