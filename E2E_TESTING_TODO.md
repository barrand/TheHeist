# E2E Testing - Remaining Work

## Current Status

The E2E testing framework is **90% complete** and functional. The core infrastructure is in place:

✅ **Completed:**
- BotPlayer with WebSocket connection and action methods
- LLMDecisionMaker for intelligent bot decisions
- NPCConversationBot for dialogue handling
- GameplayTestOrchestrator for multi-bot coordination
- Full test harness with verbose logging
- Batch testing support
- Dependencies installed (aiohttp, websockets, pydantic)

❌ **Remaining Issue:**
- **Host Assignment Problem**: Bots cannot start games because of host validation

## The Host Assignment Problem

### Root Cause

The E2E orchestrator runs in a **separate process** from the backend server:
1. Orchestrator creates room via HTTP API (creates a host player)
2. Bots connect via WebSocket as **new players** (not the HTTP host)
3. Backend rejects `start_game` because bot is not the host player
4. Tests fail with "Bot is not host, cannot start game"

### Backend Logs Show

```
2026-02-26 15:55:29 - app.api.websocket - INFO - 📨 Received start_game from player 96b77...
2026-02-26 15:55:29 - app.services.room_manager - WARNING - ❌ Player 96b77... is not host of room PONY
```

### Current Workaround Attempts

1. ❌ Direct room_manager manipulation - Doesn't work across processes
2. ❌ Empty room creation - WebSocket join logic doesn't assign host
3. ❌ Bypass host check in bot - Backend still validates

## Proposed Solutions

### Option 1: E2E Testing API Endpoint (RECOMMENDED)

Add a special endpoint for E2E testing to transfer host privileges:

```python
# backend/app/api/rooms.py
@router.post("/{room_code}/assign_host")
async def assign_host_for_testing(
    room_code: str,
    player_id: str,
    testing_token: str = Header(None)
):
    """Assign host for E2E testing (requires testing token)"""
    if testing_token != os.getenv("E2E_TESTING_TOKEN"):
        raise HTTPException(403, "Unauthorized")
    
    room_manager = get_room_manager()
    room = room_manager.get_room(room_code)
    if room:
        room.host_id = player_id
        return {"success": True}
    raise HTTPException(404, "Room not found")
```

**Pros:**
- Clean separation of concerns
- Secure (requires token)
- Works across processes
- No changes to production code

**Cons:**
- Adds testing-specific endpoint
- Requires environment variable

### Option 2: Host Rejoining Logic

Make the first bot "rejoin" as the HTTP-created host player:

```python
# In orchestrator._create_room():
room_code, host_player_id = await self._create_room()

# First bot uses host_player_id when joining
bots[0]._override_player_id = host_player_id
```

**Pros:**
- No new endpoints
- Uses existing rejoin logic

**Cons:**
- Requires bot to know host player_id
- Complex coordination
- Fragile

### Option 3: Bypass Host Check for E2E

Add an E2E mode flag to backend:

```python
# backend/app/config.py
E2E_TESTING_MODE = os.getenv("E2E_TESTING_MODE", "false").lower() == "true"

# backend/app/services/room_manager.py
def start_game(...):
    if not E2E_TESTING_MODE and not room.is_host(player_id):
        return False
```

**Pros:**
- Simple to implement
- Minimal code changes

**Cons:**
- Modifies production code path
- Could mask bugs
- Reduces test fidelity

### Option 4: First Joiner Becomes Host (CLEAN)

Modify `join_room` to assign first joiner as host if no host exists:

```python
# backend/app/services/room_manager.py
def join_room(self, room_code: str, player_name: str):
    ...
    # If room has no valid host, make first joiner the host
    if not room.host_id or room.host_id not in room.players:
        room.host_id = player_id
        logger.info(f"✅ {player_name} is now host (first joiner)")
    
    room.players[player_id] = player
    return room, player_id
```

**Pros:**
- Clean and intuitive
- No special E2E logic
- Handles edge cases (host disconnect)
- Works for production too

**Cons:**
- Changes production behavior
- Affects normal gameplay (but reasonably)

## Recommended Approach

**Use Option 4 (First Joiner Becomes Host)** because:
1. It's the cleanest solution
2. Makes sense for production (handles host disconnect)
3. No special E2E logic needed
4. Simplifies room creation flow

## Implementation Plan

### Step 1: Update room_manager.py

```python
def join_room(self, room_code: str, player_name: str) -> Optional[tuple[GameRoom, str]]:
    room = self.get_room(room_code)
    if not room:
        return None
    
    # Check if room has a valid host
    has_valid_host = room.host_id and room.host_id in room.players
    
    # Create player
    player_id = str(uuid.uuid4())
    player = Player(id=player_id, name=player_name, role=None, connected=True)
    
    # Add player to room
    room.players[player_id] = player
    
    # If no valid host, make this player the host
    if not has_valid_host:
        room.host_id = player_id
        logger.info(f"✅ {player_name} ({player_id}) joined room {room_code} as HOST (first joiner)")
    else:
        logger.info(f"✅ {player_name} ({player_id}) joined room {room_code}")
    
    return room, player_id
```

### Step 2: Update orchestrator to not create host via HTTP

```python
async def _create_room(self) -> Optional[str]:
    """Create empty room - first WebSocket joiner becomes host"""
    # Option A: Use HTTP endpoint but ignore the host player
    # Option B: Create room directly in room_manager
    # Option C: Add new endpoint that creates empty room
```

### Step 3: Test

```bash
python backend/scripts/test_gameplay_e2e.py \
  --scenario backend/scripts/output/test_scenarios/01_museum_2players.md \
  --difficulty medium \
  --verbose
```

### Step 4: Verify in logs

Should see:
```
✅ Bot_mastermind (xxx) joined room ROOM as HOST (first joiner)
✅ Bot_safe_cracker (yyy) joined room ROOM
Host (Bot_mastermind) starting game...
✅ Game started successfully
```

## Testing Checklist

Once host issue is fixed:

- [ ] Single bot can join and start game
- [ ] Two bots can join, first becomes host
- [ ] Host can start game successfully
- [ ] Game loop executes turns
- [ ] Bots make LLM decisions
- [ ] Bots complete tasks
- [ ] NPC conversations work
- [ ] Minigames auto-complete
- [ ] Test completes or times out gracefully
- [ ] Verbose logging shows all actions
- [ ] Results report is accurate

## Files to Modify

1. `backend/app/services/room_manager.py` - First joiner becomes host
2. `backend/scripts/e2e_testing/gameplay_test_orchestrator.py` - Simplified room creation
3. `backend/scripts/e2e_testing/bot_player.py` - Remove bypass warning

## Estimated Time

- Implementation: 15 minutes
- Testing: 10 minutes
- **Total: 25 minutes**

## Current Test Scenarios

We have 2 validated scenarios ready for E2E testing:

1. `backend/scripts/output/test_scenarios/01_museum_2players.md`
   - Scenario: Museum Gala Vault Heist
   - Roles: Mastermind, Safe Cracker
   - Tasks: 20+ tasks
   - Status: ✅ Passed validation

2. `backend/scripts/output/test_scenarios/02_mansion_2players.md`
   - Scenario: Mansion Panic Room
   - Roles: Mastermind, Driver
   - Tasks: 20+ tasks
   - Status: ✅ Passed validation

## Next Steps After Fix

1. Run E2E test on both scenarios
2. Watch verbose logs in real-time
3. Verify bot behavior and LLM decisions
4. Check for any gameplay issues
5. Run batch test on multiple difficulties
6. Generate more scenarios and test at scale
7. Profile performance and costs

---

**Status**: Ready to implement  
**Blocked by**: Host assignment fix  
**Priority**: High  
**Owner**: To be assigned
