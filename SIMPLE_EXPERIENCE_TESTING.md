# Simple Experience File Testing Guide

## What We Created

A hand-crafted minimal heist experience for fast testing:

**File:** `backend/examples/generated_museum_gala_vault_2players.md`

**Specs:**
- **4 tasks total** (2 per role)
- **2 players** (Mastermind + Safe Cracker)
- **3 locations** (Grand Hall, Vault Room, Museum Entrance)
- **Linear flow** with simple dependencies
- **No discovery system** (all tasks visible from start)
- **~300 words** (vs. 2,500 in AI-generated version)

## Task Breakdown

### Mastermind (2 tasks)
1. **💬 NPC** - Distract the Guard
   - Talk to security guard in Grand Hall
   - No dependencies (starting task)

2. **🗣️ INFO** - Share Vault Location
   - Radio Safe Cracker with intel
   - Depends on: Task 1 (guard distracted)

### Safe Cracker (2 tasks)
1. **💬 NPC** - Access the Vault Area
   - Navigate to vault while guard is busy
   - Depends on: MM Task 1 (guard distracted)

2. **🎮 MINIGAME** - Crack the Vault (dial_rotation)
   - Crack the combination lock
   - Depends on: Task 1 (vault accessed) + MM Task 2 (location confirmed)

## Dependency Flow

```
START
  ├─> MM1: Distract Guard (💬 NPC)
  │     ├─> MM2: Share Location (🗣️ INFO)
  │     │     └─> SC2: Crack Vault (🎮 dial_rotation)
  │     └─> SC1: Access Vault (💬 NPC)
  │           └─> SC2: Crack Vault (🎮 dial_rotation)
  └─> COMPLETE
```

## How to Test

### 1. Backend Status
✅ Backend running on http://localhost:8000
✅ Experience file loaded: `generated_museum_gala_vault_2players.md`

### 2. Start Game Flow

**Browser 1 (Host - Mastermind):**
1. Open Flutter app: `http://localhost:8088` (or your port)
2. Create Room → Enter name
3. Auto-assigned: Mastermind ✅
4. Scenario: Museum Gala (default) ✅
5. Wait for player 2

**Browser 2 (Player - Safe Cracker):**
1. Open Flutter app: `http://localhost:8089` (different port)
2. Join Room → Enter code + name
3. Auto-assigned: Safe Cracker ✅
4. Ready!

**Host clicks "Start Game"**
- ✅ 2 players = minimum met
- ✅ Both have roles
- ✅ Experience file: `generated_museum_gala_vault_2players.md`
- 🎮 **Game begins!**

### 3. Expected Game Screen

**Mastermind sees:**
- Team Objective: "Steal the Eye of Orion jewels from the museum vault"
- YOUR TASKS:
  - [ ] MM1: Distract the Guard (💬 NPC) - AVAILABLE
  - [ ] MM2: Share Vault Location (🗣️ INFO) - LOCKED

**Safe Cracker sees:**
- Team Objective: "Steal the Eye of Orion jewels from the museum vault"
- YOUR TASKS:
  - [ ] SC1: Access the Vault Area (💬 NPC) - LOCKED (needs MM1)
  - [ ] SC2: Crack the Vault (🎮 dial_rotation) - LOCKED (needs SC1 + MM2)

### 4. Test Sequence

**Step 1: Mastermind completes MM1 (Distract Guard)**
- Click task → Opens NPC chat
- Talk to Security Guard
- Complete task ✅
- MM2 should unlock
- SC1 should unlock

**Step 2: Mastermind completes MM2 (Share Location)**
- Click task → Info share (radio Safe Cracker)
- Complete task ✅
- SC2 should unlock (once SC1 is also done)

**Step 3: Safe Cracker completes SC1 (Access Vault)**
- Click task → NPC interaction (navigate to vault)
- Complete task ✅
- SC2 should now be available

**Step 4: Safe Cracker completes SC2 (Crack Vault)**
- Click task → Opens `dial_rotation` minigame
- Complete minigame ✅
- **HEIST COMPLETE!** 🎉

### 5. What to Watch For

**UI Issues:**
- [ ] Do all 4 tasks display correctly?
- [ ] Are dependencies working (locked/unlocked)?
- [ ] Do NPC dialogs appear?
- [ ] Does the dial_rotation minigame trigger?
- [ ] Do task icons show correct emoji?

**Backend Issues:**
- [ ] Check backend logs for errors
- [ ] Verify task status updates via WebSocket
- [ ] Confirm completion tracking works

**Game Flow Issues:**
- [ ] Can both players see their tasks?
- [ ] Do tasks unlock in correct order?
- [ ] Does completion logic work?

## Comparison: Simple vs. AI-Generated

| Feature | Simple (Manual) | AI-Generated |
|---------|----------------|--------------|
| Tasks | 4 | 23 |
| Locations | 3 | 15 |
| NPCs | 2 | Multiple with personalities |
| Discovery System | No | Yes (6 moments) |
| Task Spawning | No | Yes |
| Mermaid Diagrams | 1 (simple) | 2 (full + simplified) |
| File Size | 2.9KB | 18KB |
| Playtime | 2-3 minutes | 15-20 minutes |
| Purpose | Fast testing | Full gameplay |

## Next Steps

### If It Works ✅
1. Document what made it successful
2. Create 2-3 more simple experiences by hand
3. Extract patterns
4. Build automated generator
5. Return to AI for complex experiences

### If Issues Found ❌
1. Check backend logs in terminal
2. Review ExperienceLoader parsing
3. Verify task format matches expectations
4. Fix issues in the `.md` file
5. Restart backend and retest

## Key Files

- **Experience File:** [`backend/examples/generated_museum_gala_vault_2players.md`](backend/examples/generated_museum_gala_vault_2players.md)
- **Backend Loader:** [`backend/app/services/experience_loader.py`](backend/app/services/experience_loader.py)
- **WebSocket Handler:** [`backend/app/api/websocket.py`](backend/app/api/websocket.py)
- **Game Screen:** [`app/lib/screens/game_screen.dart`](app/lib/screens/game_screen.dart)
- **Room Lobby:** [`app/lib/screens/room_lobby_screen.dart`](app/lib/screens/room_lobby_screen.dart)

## Backend Status Check

```bash
# Check backend is running
curl http://localhost:8000/health

# Check backend logs
tail -f ~/.cursor/projects/Users-bbarrand-Documents-Projects-TheHeist/terminals/412023.txt
```

## Success Criteria

- ✅ Backend loads experience without errors
- ✅ Game starts with 2 players
- ✅ All 4 tasks display correctly
- ✅ Dependencies lock/unlock properly
- ✅ NPC dialogs work
- ✅ Minigame triggers
- ✅ Completion tracking works
- ✅ Can play from start to finish in 2-3 minutes

---

**Status:** Backend ready, experience file created, ready to test in Flutter app!
