# E2E Testing Quick Start

Get started with automated gameplay testing in 5 minutes!

## 1. Prerequisites

✅ **Backend running**:
```bash
cd backend
uvicorn app.main:app --reload
```

✅ **Gemini API Key** in `.env` file

✅ **Dependencies installed**:
```bash
pip install websockets aiohttp google-generativeai
```

## 2. Test a Single Scenario

```bash
# Test a 3-player bank heist scenario
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario backend/scripts/output/test_scenarios/06_bank_3players.md
```

**What happens:**
1. Creates game room
2. Spawns 3 bots (Mastermind, Hacker, Safe Cracker)
3. Bots join room and select roles
4. Host starts game
5. Bots take turns completing tasks
6. Reports win/deadlock/timeout

**Expected output (live monitoring):**
```
12:34:56 [    INFO] Starting E2E Gameplay Test
12:34:57 [    INFO] Scenario: Bank Safe Deposit Box Heist
12:34:58 [    INFO] Created room: TIGER
12:35:00 [    INFO] Connecting 3 bots...
12:35:05 [    INFO] Starting main game loop...

12:35:06 [    INFO] --- Turn 1 ---
12:35:07 [    INFO]   👤 Mastermind @ safe_house
12:35:08 [    INFO]      → Move to bank_lobby
12:35:08 [    INFO]      ✅ Success
12:35:09 [    INFO]   👤 Hacker @ safe_house
12:35:10 [    INFO]      → Move to bank_lobby
12:35:10 [    INFO]      ✅ Success
...

12:40:15 [    INFO] ============================================================
12:40:15 [    INFO]   TURN 35 / 500
12:40:15 [    INFO]   Active: 2/3 bots
12:40:15 [    INFO]   Completed: 18 tasks
12:40:15 [    INFO] ============================================================

...

12:42:15 [    INFO] 🎉 ============================================================
12:42:15 [    INFO]    ✅ GAME WON IN 42 TURNS!
12:42:15 [    INFO]    ============================================================

===== GAMEPLAY TEST RESULT =====
Scenario: Bank Safe Deposit Box Heist (3 players, medium)
Status: WIN (42 turns)

Per-Role Performance:
  Mastermind: 6 tasks, 2 NPC conversations, 3 idle turns
  Hacker: 7 tasks, 1 NPC conversations, 4 idle turns
  Safe Cracker: 5 tasks, 0 NPC conversations, 5 idle turns
```

**You'll see:**
- 👤 Each bot's turn
- → What action they choose
- ✅/❌ Whether it succeeds
- Progress summaries every 5 turns
- 🎉 Win celebration!

**For more details, add `--verbose`:**
```bash
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario scenarios/bank_heist.md \
  --verbose
```

See **[MONITORING_E2E_TESTS.md](MONITORING_E2E_TESTS.md)** for complete monitoring guide.

## 3. Test All Difficulties

```bash
# Test easy, medium, and hard
python3 backend/scripts/batch_gameplay_test.py \
  --scenarios backend/scripts/output/test_scenarios/06_bank_3players.md \
  --all-difficulties
```

**Output shows pass/fail for each difficulty:**
```
EASY:
  1/1 scenarios passed (100%)

MEDIUM:
  1/1 scenarios passed (100%)

HARD:
  0/1 scenarios passed (0%)
  Failed scenarios:
    - Bank Safe Deposit Box Heist: TIMEOUT (45 turns)
      • NPC conversations too difficult
```

## 4. Batch Test Multiple Scenarios

```bash
# Test all scenarios in directory
python3 backend/scripts/batch_gameplay_test.py \
  --scenarios backend/scripts/output/test_scenarios/*.md \
  --difficulties medium
```

## 5. Full Validation + Gameplay Test

```bash
# Run structural validation first, then gameplay test
python3 backend/scripts/full_scenario_test.py \
  --scenario backend/scripts/output/test_scenarios/06_bank_3players.md
```

**This pipeline:**
1. ✅ Structural validation (fast)
2. ✅ E2E gameplay test (thorough)
3. Combined report

## Understanding Results

### Status Types

- **WIN** ✅ - All tasks completed successfully
- **DEADLOCK** ⚠️ - Bots have no available tasks (stuck)
- **TIMEOUT** ⚠️ - Reached 500 turns without completing
- **ERROR** ❌ - Technical failure

### Common Issues

**"DEADLOCK after 15 turns"**
→ Check scenario prerequisites - some tasks may be unreachable

**"TIMEOUT - NPC conversations too difficult"**
→ Hard difficulty may be too hard, or NPC requires specific outcomes

**"Failed to connect"**
→ Make sure backend is running on localhost:8000

## Next Steps

- Read full docs: `backend/scripts/E2E_TESTING_README.md`
- Test your own scenarios
- Integrate with CI/CD
- Generate reports for playtesting

## Architecture at a Glance

```
You run test → Orchestrator spawns bots → Bots play game → Report generated

For 8-player scenario:
  8 bots × WebSocket connections → Backend → Win/Fail result
```

Each bot:
- Uses Gemini to make decisions
- Completes tasks, talks to NPCs
- Works as a team
- Reports detailed metrics

## Cost

Per test (2-3 players, ~30 turns):
- **~$0.02** using Gemini 2.5 Flash

Batch test (10 scenarios × 3 difficulties):
- **~$0.60** total

Very affordable for comprehensive testing!
