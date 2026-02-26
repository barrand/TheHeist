# E2E Gameplay Testing Framework

Automated end-to-end testing framework that spawns bot players to complete full scenario playthroughs.

## Overview

The E2E testing framework validates scenarios by actually playing them with LLM-powered bot players that:
- Connect via WebSocket like real players
- Analyze game state and make intelligent decisions
- Complete tasks, talk to NPCs, search for items
- Work as a team to complete the heist

This catches issues that structural validation cannot detect:
- **NPC conversation impossibility** - Target outcomes can't be achieved
- **Item search issues** - Items defined but not actually findable
- **Prerequisite timing issues** - Unlock order makes game unwinnable
- **Hidden deadlocks** - Specific action sequences cause progress blocks
- **Actual playthrough time** - Scenario takes too long or too short

## Architecture

```
┌─────────────────────────────────────────────┐
│      Gameplay Test Orchestrator            │
│  - Creates room                            │
│  - Spawns N bots (one per role)           │
│  - Coordinates turns                       │
│  - Monitors progress                       │
└──────────────┬──────────────────────────────┘
               │
     ┌─────────┴──────────────┐
     │                        │
┌────▼─────┐            ┌────▼─────┐
│ Bot #1   │            │ Bot #N   │
│ Mastermind│           │ Hacker   │
└────┬─────┘            └────┬─────┘
     │                        │
     │    WebSocket           │
     └────────┬───────────────┘
              │
         ┌────▼─────┐
         │ Backend  │
         │ API      │
         └──────────┘
```

Each bot:
1. Connects via WebSocket
2. Receives tasks and game state
3. Uses LLM to decide actions
4. Executes actions
5. Monitors for completion/failure

## Components

### 1. BotPlayer (`bot_player.py`)

Simulates a single player:
- WebSocket connection to `/ws/{room_code}`
- Maintains local game state (tasks, inventory, location)
- Action methods: `move_to_location()`, `search_location()`, `pickup_item()`, `complete_task()`, `talk_to_npc()`, `handoff_item()`

### 2. LLMDecisionMaker (`llm_decision_maker.py`)

Makes intelligent decisions:
- Analyzes available tasks, prerequisites, inventory
- Considers critical path and team coordination
- Uses Gemini 2.5 Flash for fast, economical decisions
- Returns `ActionDecision` with reasoning

### 3. NPCConversationBot (`npc_conversation_bot.py`)

Handles NPC conversations:
- Chooses appropriate cover story
- Analyzes quick-response options
- Uses LLM to select best responses
- Monitors suspicion level
- Continues until outcomes achieved or failure

### 4. GameplayTestOrchestrator (`gameplay_test_orchestrator.py`)

Coordinates full test:
- Parses scenario file
- Creates room via REST API
- Spawns N bots (automatically scaled by player count)
- Runs main game loop
- Detects win/deadlock/timeout
- Generates detailed report

## Multi-Player Scaling

The framework **automatically scales** to match the scenario:

- **2-player scenario** → Spawns 2 bots
- **8-player scenario** → Spawns 8 bots
- **12-player scenario** → Spawns 12 bots

Each bot:
- Has its own WebSocket connection
- Receives its role-specific tasks
- Makes independent decisions
- Coordinates with teammates (handoffs, info shares)

Example for 8-player scenario:
```python
# Orchestrator detects 8 roles from scenario
roles = ["Mastermind", "Hacker", "Safe Cracker", "Driver", "Insider", "Grifter", "Muscle", "Lookout"]

# Spawns 8 bots
bots = [BotPlayer(name=f"Bot_{role}", role=role) for role in roles]

# All connect concurrently
await asyncio.gather(*[bot.connect(room_code) for bot in bots])

# Game loop coordinates all 8 bots
```

## Difficulty Level Testing

Tests all 3 difficulty levels automatically:

**How difficulty affects bots:**
- **Easy**: NPC conversations start with suspicion=0, forgiving
- **Medium**: Suspicion=2, moderate penalties
- **Hard**: Suspicion=3, strict penalties, NPCs less helpful

**Testing command:**
```bash
# Test all difficulties for one scenario
python3 batch_gameplay_test.py \
  --scenarios scenarios/museum_heist.md \
  --all-difficulties
```

**Example report:**
```
EASY:
  10/10 scenarios passed (100%)

MEDIUM:
  8/10 scenarios passed (80%)
  Failed scenarios:
    - Museum Gala: TIMEOUT (45 turns)
      • NPC conversation took too long

HARD:
  5/10 scenarios passed (50%)
  Failed scenarios:
    - Bank Heist: DEADLOCK (32 turns)
      • Guard NPC conversation impossible to complete
```

## Usage

### Prerequisites

1. **Backend must be running:**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Install dependencies:**
```bash
pip install websockets aiohttp google-generativeai python-dotenv
```

3. **Gemini API Key** must be in `.env` file

### Test Single Scenario

```bash
# Test one scenario at medium difficulty
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario backend/experiences/generated_museum_2players.md

# Test at hard difficulty
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario backend/experiences/generated_museum_2players.md \
  --difficulty hard

# Verbose logging
python3 backend/scripts/test_gameplay_e2e.py \
  --scenario scenarios/bank_heist.md \
  --verbose
```

### Batch Test Multiple Scenarios

```bash
# Test all scenarios in directory
python3 backend/scripts/batch_gameplay_test.py \
  --scenarios backend/scripts/output/test_scenarios/*.md

# Test all difficulties
python3 backend/scripts/batch_gameplay_test.py \
  --scenarios backend/scripts/output/test_scenarios/*.md \
  --all-difficulties

# Test specific difficulties
python3 backend/scripts/batch_gameplay_test.py \
  --scenarios scenarios/*.md \
  --difficulties easy medium

# Parallel testing (faster but uses more resources)
python3 backend/scripts/batch_gameplay_test.py \
  --scenarios scenarios/*.md \
  --parallel 3
```

### Integration with Existing Validation

```bash
# Full pipeline: Generate → Validate structure → Test gameplay
python3 backend/scripts/full_scenario_pipeline.py \
  --scenario museum_gala_vault \
  --roles mastermind safe_cracker \
  --test-gameplay
```

## Test Results

### GameplayTestResult

Each test produces a detailed result:

```python
{
  "scenario_file": "scenarios/museum_heist.md",
  "scenario_name": "Museum Gala Vault Heist",
  "player_count": 2,
  "difficulty": "medium",
  
  "status": "WIN",  # WIN, DEADLOCK, TIMEOUT, ERROR
  "turns_taken": 35,
  
  "tasks_completed_per_role": {
    "Mastermind": 5,
    "Safe Cracker": 4
  },
  
  "idle_turns_per_role": {
    "Mastermind": 3,
    "Safe Cracker": 5
  },
  
  "npc_conversations_per_role": {
    "Mastermind": [
      {"success": True, "turns": 8, "outcomes": ["vault_access"]},
      {"success": True, "turns": 5, "outcomes": ["guard_distracted"]}
    ]
  },
  
  "issues": [
    "Turn 15-18: Safe Cracker idle (waiting for Mastermind)"
  ],
  
  "game_log": [...]
}
```

### Status Types

- **WIN**: All tasks completed successfully
- **DEADLOCK**: No bots have available tasks (stuck)
- **TIMEOUT**: Reached max turns (500) without completing
- **ERROR**: Technical failure (connection, parsing, etc.)

## Example Output

```
===== GAMEPLAY TEST RESULT =====
Scenario: Museum Gala Vault Heist (2 players, medium)
Status: WIN (35 turns)

Per-Role Performance:
  Mastermind: 5 tasks, 2 NPC conversations, 3 idle turns
  Safe Cracker: 4 tasks, 1 minigame, 5 idle turns

Issues Detected:
  - Turn 15-18: Safe Cracker idle (waiting for Mastermind)
  - Turn 22: MM4 (Convince Guard) took 8 conversation turns

Recommendations:
  - Add parallel task for Safe Cracker during MM4
  - Consider adding alternative path to avoid guard
```

## Benefits Over Structural Validation

### Structural Validation (Fast)
✅ Checks references exist
✅ Validates dependencies
✅ Simulates task flow
❌ Can't test NPC conversations
❌ Can't verify item searchability
❌ Can't detect subtle deadlocks

### E2E Gameplay Testing (Thorough)
✅ Actually plays the scenario
✅ Tests NPC conversations with LLM
✅ Verifies items are findable
✅ Detects real deadlocks
✅ Measures actual playtime
✅ Tests difficulty balance
✅ Tests all player counts (2-12)

**Use both:** Structural validation first (fast, catches obvious issues), then E2E testing (slower, catches gameplay issues).

## Performance

### Single Test
- **Time**: 2-15 minutes depending on scenario complexity
- **Cost**: ~$0.05-0.20 per test (Gemini Flash API calls)
- **Tokens**: ~50-200k tokens per test

### Batch Testing
- **Sequential**: Safe, predictable, slower
- **Parallel**: Faster but uses more memory/connections
- Recommendation: `--parallel 3` for good balance

### Optimization Tips
1. Use structural validation first to catch obvious issues
2. Test 2-player scenarios before 10-player (cheaper)
3. Test medium difficulty first, then hard
4. Use `--parallel` for large batches
5. Fix common issues before large batch tests

## Troubleshooting

### "Failed to connect"
- Check backend is running on localhost:8000
- Check WebSocket endpoint is accessible

### "Failed to start game"
- Verify scenario file exists and is valid
- Check scenario_id matches file metadata

### "DEADLOCK after few turns"
- Check scenario has proper prerequisites
- Run structural validation first
- Check if items are actually searchable

### "LLM decision error"
- Check Gemini API key is valid
- Check API quota/rate limits
- Temporary network issue - retry

### "TIMEOUT"
- Scenario may be too long (500 turns is limit)
- Check for circular dependencies
- NPC conversations may be too difficult

## Future Enhancements

- [ ] Listen for `game_ended` WebSocket message for win detection
- [ ] Track team coordination metrics (handoffs, info shares)
- [ ] Compare bot performance vs human playtime
- [ ] Generate visual playthrough reports
- [ ] Support for twist events (once implemented)
- [ ] Replay failed tests for debugging
- [ ] Bot decision strategy selection (intelligent/greedy/random)

## Cost Estimation

**Per test** (medium complexity, 2 players, ~30 turns):
- Decision making: ~100 LLM calls @ $0.0001/call = $0.01
- NPC conversations: 5 conversations × 10 calls = $0.005
- **Total**: ~$0.02 per test

**Batch test** (10 scenarios × 3 difficulties = 30 tests):
- **Total**: ~$0.60

**Note**: Using Gemini 2.5 Flash (most economical model)
