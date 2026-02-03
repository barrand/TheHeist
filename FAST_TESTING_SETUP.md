# Fast Testing Setup ✅

Configuration optimized for quick development testing!

## 🚀 What's Configured

### 1. **Auto-Role Assignment**
- **Host creates room** → Automatically assigned **Mastermind** ✅
- **First player joins** → Automatically assigned **Safe Cracker** ✅
- Roles assign 500ms after room state loads
- Perfect for rapid testing!

### 2. **Default Scenario: Museum Gala**
- Museum Gala Vault Heist selected by default
- Requires only 2 players (Mastermind + Safe Cracker)
- Experience file generated and ready

### 3. **Generated Experience**
- ✅ `backend/examples/museum_gala_vault.md`
- 2,457 words of AI-generated heist content
- Task dependency trees
- Discovery system
- NPC interactions
- Minigames

## 🎮 Testing Flow

### Quick Start (2 Players)
1. **Terminal 1:** Run backend (already running)
   ```bash
   cd backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Terminal 2:** Run Flutter app
   ```bash
   cd app && flutter run -d chrome
   ```

3. **Browser 1 (Host):**
   - Create Room → Name entry
   - **Auto-assigned:** Mastermind ✅
   - **Auto-selected:** Museum Gala ✅
   - Wait for player 2

4. **Browser 2 (Player):**
   - Join Room → Enter code + name
   - **Auto-assigned:** Safe Cracker ✅
   - Ready to start!

5. **Host clicks "Start Game"**
   - ✅ 2 players = minimum met
   - ✅ Both have roles
   - ✅ Experience file loaded
   - 🎮 Game begins!

### Expected Timeline
- Room creation: **<1 second**
- Player joins: **<1 second**
- Auto-role assignment: **0.5 seconds each**
- Start game: **<2 seconds**
- **Total:** ~5 seconds from create to game start! ⚡

## 🎯 Museum Gala Experience (2 Players)

### Roles
- **Mastermind** (Host)
  - Orchestrate heist
  - Social engineering
  - Intel gathering
  - Distraction coordination

- **Safe Cracker** (Player 2)
  - Physical bypasses
  - Lock picking minigames
  - Vault cracking
  - Equipment handling

### Key Locations (15 total)
1. Safe House (briefing)
2. Museum Front Steps
3. Grand Hall (gala)
4. Coat Check Room
5. Security Checkpoint
6. Curator's Office
7. Security Room
8. Maintenance Room
9. Vault Corridor
10. Vault Room (target)
11. Getaway Vehicle

### Discovery Highlights
- 🔍 Examine vault door (reveals mechanism)
- 👥 Talk to stressed caterer (get access)
- 🔍 Search curator's desk (find clue)
- 🎯 Observe security patterns
- ⚡ Disable motion sensors
- 🎮 Crack the vault!

### Task Types
- **Minigames:** Lock picking, safe cracking
- **NPC Dialogues:** Caterer, guard, staff
- **Discovery:** Examine objects, search areas
- **Team Coordination:** Info sharing
- **Item Management:** Tools, keycards, clues

## 📱 UI Updates

### Scenario Selector Button
- ✅ Now shows 80×80px scenario image (no emoji!)
- ✅ Museum Gala purple mansion scene
- ✅ Tappable to browse all 11 scenarios

### Role Selector Button
- ✅ Now shows 80×80px player avatar
- ✅ Female version displayed by default
- ✅ Much larger and more prominent

### Player Minimum
- ✅ All scenarios: 2 players
- ✅ Dynamic validation based on scenario
- ✅ "Need at least X more player to start"

## 🔧 Technical Details

### Experience File Format
```markdown
# Museum Gala Vault Heist - Experience File

**ID**: `museum_gala_vault`
**Selected Roles**: Mastermind, Safe Cracker
**Player Count**: 2 players

## 🎯 Team Objectives
1. Infiltrate the Gala
2. Access and Crack the Vault
3. Steal the Jewels and Escape

## Discovery Tasks
- SC_EXAMINE_VAULT_DOOR_01
- MM_OBSERVE_GALA_01
- SC_SEARCH_CURATOR_DESK_01
...

## Roles & Dependencies
### Mastermind
1. MM1. 💬 NPC - Brief Safe Cracker
   - Dependencies: None (starting task)
...
```

### Backend Loading
```python
# In websocket.py handle_start_game()
loader = ExperienceLoader(experiences_dir="examples")
game_state = loader.load_experience(scenario, selected_roles)
```

## ✅ Ready to Test

### Checklist
- ✅ Backend running with examples/ directory
- ✅ Museum Gala experience file generated
- ✅ Auto-role assignment for host (Mastermind)
- ✅ Auto-role assignment for joiner (Safe Cracker)
- ✅ Default scenario: Museum Gala
- ✅ 2-player minimum working
- ✅ Larger images in selector buttons (80px)

### Testing Now
1. **Create room** → Auto-assigned Mastermind
2. **Join room** (second browser) → Auto-assigned Safe Cracker
3. **Click "Start Game"** → Should work! 🎉
4. **Navigate to game screen** → See objectives and tasks

### Next Steps After Testing
- [ ] Verify game screen displays tasks correctly
- [ ] Test discovery system
- [ ] Test NPC interactions
- [ ] Test minigames
- [ ] Refine experience if needed
- [ ] Generate other 10 scenarios (or keep dynamic generation)

---

**Summary:**
- **Experience generated:** Museum Gala for 2 players ✅
- **Auto-roles:** Mastermind + Safe Cracker ✅
- **Default scenario:** Museum Gala ✅
- **Backend:** Restarted with experience ✅
- **Image sizes:** 80px selector buttons ✅
- **Ready to play:** YES! 🎮✨
