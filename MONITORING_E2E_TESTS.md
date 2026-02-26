# Monitoring E2E Tests in Real-Time

You can watch the entire simulation as it happens! Here's what you'll see:

## Standard Output (Default)

When you run a test, you'll see a **live play-by-play**:

```bash
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario backend/scripts/output/test_scenarios/06_bank_3players.md
```

**Example output:**

```
12:34:56 [    INFO] ============================================================
12:34:56 [    INFO] Starting E2E Gameplay Test
12:34:56 [    INFO] Scenario: backend/scripts/output/test_scenarios/06_bank_3players.md
12:34:56 [    INFO] Difficulty: medium
12:34:56 [    INFO] Backend: http://localhost:8000
12:34:56 [    INFO] ============================================================
12:34:57 [    INFO] Scenario: Bank Safe Deposit Box Heist
12:34:57 [    INFO] Roles: ['Mastermind', 'Hacker', 'Safe Cracker']
12:34:57 [    INFO] Difficulty: medium
12:34:58 [    INFO] Created room: TIGER
12:34:59 [    INFO] Connecting 3 bots...
12:35:01 [    INFO] Bot Bot_Mastermind joined as player_123, host=True
12:35:01 [    INFO] Bot Bot_Hacker joined as player_456, host=False
12:35:01 [    INFO] Bot Bot_Safe_Cracker joined as player_789, host=False
12:35:02 [    INFO] Bots selecting roles...
12:35:03 [    INFO] Host (Bot_Mastermind) starting game...
12:35:05 [    INFO] Bot Bot_Mastermind received 6 tasks
12:35:05 [    INFO] Starting main game loop...

12:35:06 [    INFO] 
12:35:06 [    INFO] --- Turn 1 ---
12:35:07 [    INFO]   👤 Mastermind @ safe_house
12:35:07 [    INFO]      → Move to bank_lobby
12:35:08 [    INFO]      ✅ Success
12:35:08 [    INFO]   👤 Hacker @ safe_house
12:35:09 [    INFO]      → Move to bank_lobby
12:35:09 [    INFO]      ✅ Success
12:35:10 [    INFO]   👤 Safe Cracker @ safe_house
12:35:10 [    INFO]      → Search location
12:35:11 [    INFO]      ✅ Success

12:35:12 [    INFO] 
12:35:12 [    INFO] --- Turn 2 ---
12:35:13 [    INFO]   👤 Mastermind @ bank_lobby
12:35:14 [    INFO]      → Complete task MM1
12:35:15 [    INFO]      ✅ Success
12:35:15 [    INFO]   👤 Hacker @ bank_lobby
12:35:16 [    INFO]      → Complete task H1
12:35:17 [    INFO]      ✅ Success

...

12:40:15 [    INFO] 
12:40:15 [    INFO] ============================================================
12:40:15 [    INFO]   TURN 35 / 500
12:40:15 [    INFO]   Active: 2/3 bots
12:40:15 [    INFO]   Completed: 18 tasks
12:40:15 [    INFO] ============================================================

...

12:42:30 [    INFO] 
12:42:30 [    INFO] 🎉 ============================================================
12:42:30 [    INFO]    ✅ GAME WON IN 42 TURNS!
12:42:30 [    INFO]    ============================================================
```

## Verbose Mode (More Details)

Add `--verbose` flag to see LLM decision reasoning:

```bash
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario scenarios/bank_heist.md \
  --verbose
```

**Additional output includes:**
- Why each bot chose their action
- Available tasks at each decision point
- WebSocket message details
- Backend API responses

**Example verbose output:**

```
12:35:07 [   DEBUG]      Available tasks: 6
12:35:08 [   DEBUG]      Reasoning: Moving to bank_lobby to start reconnaissance and gather initial information about the target
12:35:09 [   DEBUG] Bot Bot_Mastermind moved to bank_lobby
```

## What You'll See

### 1. **Setup Phase** (First 10 seconds)
- Room creation
- Bots connecting
- Role selection
- Game start

### 2. **Main Game Loop** (Most of the time)
- **Every Turn**: Which bots are active, what they decide to do, whether it succeeds
- **Every 5 Turns**: Progress summary (turn count, active bots, completed tasks)
- **Idle Bots**: Which bots are waiting for others

### 3. **End Game**
- Win/deadlock/timeout status
- Final statistics
- Issues detected

## Log to File (Save for Review)

Redirect output to a file while still watching:

```bash
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario scenarios/bank_heist.md \
  2>&1 | tee test_run.log
```

This saves everything to `test_run.log` while showing it on screen.

## Tail in Real-Time (If Running in Background)

If you run the test in background:

```bash
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario scenarios/bank_heist.md \
  > test_run.log 2>&1 &
```

Then watch it live:

```bash
tail -f test_run.log
```

## What Each Symbol Means

- **👤** - Bot player taking action
- **→** - Action being performed
- **✅** - Action succeeded
- **❌** - Action failed
- **⚠️** - Warning or issue
- **🎉** - Game won!

## Monitoring Multiple Tests

For batch tests, you get a summary view:

```bash
python3 backend/scripts/batch_gameplay_test.py \
  --scenarios scenarios/*.md \
  --all-difficulties
```

**Output:**

```
12:45:00 [    INFO] Running 9 tests (3 scenarios × 3 difficulties)
12:45:01 [    INFO] Test 1/9: museum_heist.md @ easy
12:45:03 [    INFO] Testing museum_heist.md @ easy...
...
12:48:45 [    INFO] ✅ WIN in 28 turns
12:48:46 [    INFO] Test 2/9: museum_heist.md @ medium
...

BATCH TEST RESULTS
================================================================================

EASY:
  3/3 scenarios passed (100%)

MEDIUM:
  3/3 scenarios passed (100%)

HARD:
  1/3 scenarios passed (33%)
  Failed scenarios:
    - Bank Heist: TIMEOUT (45 turns)
      • NPC conversation took too long
```

## Monitoring Tips

### 1. **Quick Check**
Just watch for status symbols:
- Lots of ✅ = Good progress
- ❌ appearing = Something's wrong
- Long pauses = LLM thinking or stuck

### 2. **Progress Tracking**
Every 5 turns shows:
- Current turn / max turns
- How many bots are active
- Total tasks completed

### 3. **Spotting Issues**
Watch for:
- **"Idle:"** appearing repeatedly → Player stuck
- **Turn count climbing without task completions** → Deadlock approaching
- **Same bot failing repeatedly** → Possible bug

### 4. **Performance Monitoring**
- **Fast turns (< 2 sec)** = Simple actions (move, search)
- **Slow turns (5-10 sec)** = LLM decision making
- **Very slow (15+ sec)** = NPC conversation

## Example: Watching an 8-Player Game

```
--- Turn 1 ---
  👤 Mastermind @ safe_house
     → Move to museum_entrance
     ✅ Success
  👤 Hacker @ safe_house
     → Move to server_room
     ✅ Success
  👤 Safe Cracker @ safe_house
     → Search location
     ✅ Success
  👤 Driver @ parking_lot
     → Complete task D1
     ✅ Success
  👤 Insider @ museum_entrance
     → Complete task I1
     ✅ Success
  👤 Grifter @ museum_lobby
     → Complete task G1
     ✅ Success
  👤 Muscle @ safe_house
     → Wait (no available actions)
     ✅ Success
  👤 Lookout @ surveillance_point
     → Complete task L1
     ✅ Success
```

You'll see all 8 bots taking actions in parallel!

## Interrupting a Test

Press `Ctrl+C` to stop a running test:

```
^C
12:50:00 [    INFO] Test interrupted by user
```

The test will attempt to disconnect bots gracefully.

## Summary

**To monitor your E2E tests:**
1. Just run the script normally (shows live progress)
2. Add `--verbose` for more details
3. Use `| tee logfile.log` to save output
4. Watch for ✅/❌ symbols for quick status
5. Check progress summaries every 5 turns

You'll see exactly what each bot is thinking and doing in real-time! 🎮
