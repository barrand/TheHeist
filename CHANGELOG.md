# The Heist - Changelog

## 2026-02-04 - NPC System & Project Reorganization

### Major Features Added

#### 1. WHO'S HERE Section ✅
- Shows other players in your current location
- Shows NPCs in your current location
- Real-time updates when players move
- Displays player names with roles (e.g., "Sam (Safe Cracker)")
- Displays NPC names with job roles
- Only appears when others are present

#### 2. Structured NPC Format ✅
- Comprehensive NPC definitions in experience files
- All info needed for image generation AND AI conversations
- Added 2 NPCs to museum heist:
  - **Marcus Romano** (Security Guard) at Grand Hall
  - **Dr. Elena Vasquez** (Museum Curator) at Grand Hall

**NPC Information Includes:**
- Visual details: age, gender, ethnicity, clothing, expression
- Personality description for AI conversations
- Information known (HIGH/MEDIUM/LOW confidence)
- Conversation hints (how to interact effectively)
- Location (for WHO'S HERE display)

#### 3. Map View Improvements ✅
- All players see ALL locations (not just where they have tasks)
- Backend sends complete location list to all players
- Enables exploration and team coordination
- Players can travel to any accessible location

### Project Organization ✅

#### Directory Restructure
- `app/` → `frontend/` (clear naming)
- `scripts/` → `backend/scripts/` (Python tools with backend)
- `examples/` → `docs/examples/` (docs together)
- `data/` → `shared_data/` (clearer purpose)
- `backend/examples/` → `backend/experiences/` (playable files)
- Deleted: `ui/` and `prototype/` (old cruft)
- Kept: `image_playground/` (actively used)

#### Clean Structure
```
/frontend/              ← Flutter app
/backend/
  /app/                 ← Server code
  /scripts/             ← Content generation
  /experiences/         ← Playable experience files
/shared_data/           ← Shared configuration (roles, scenarios)
/image_playground/      ← Image generation tool
/design/                ← Design documentation
/docs/                  ← Technical documentation
```

### Bug Fixes

#### Location Mismatch Fix ✅
- **Issue**: Frontend looked for "Crew Hideout", backend used "Safe House"
- **Fix**: Updated frontend to use "Safe House" consistently
- **Impact**: WHO'S HERE section now correctly shows other players

#### WHO'S HERE Data Flow ✅
- **Issue**: Player list not passed from lobby to game screen
- **Fix**: Added allPlayers and myPlayerId parameters to GameScreen
- **Impact**: WHO'S HERE displays immediately on game start

### Technical Improvements

#### Backend
- ExperienceLoader parses structured NPC sections
- Sends NPCs to frontend in game_started message
- Sends all locations (not just player-specific)
- NPC conversation service ready for structured NPCs

#### Frontend
- Receives and displays NPCs from backend
- Filters NPCs by current location
- Symlink from frontend/assets/data to shared_data
- Debug logging for NPCs and locations

### Documentation

#### New Documents
- `backend/experiences/NPC_FORMAT.md` - Complete NPC format guide
- `backend/experiences/README.md` - Experience file organization
- `shared_data/README.md` - Shared data explanation
- `docs/examples/README.md` - Design examples clarification

#### Updated Documents
- `ProjectOverview.md` - New directory structure
- `design/dependency_tree_design_guide.md` - Updated paths
- `docs/MODEL_CONFIGURATION.md` - Updated script paths
- All README files reflect new organization

### Breaking Changes
- Experience files now require `## NPCs` section
- Old NPC format (inline with tasks) deprecated but still supported
- Scripts moved to `backend/scripts/` (update paths)
- Frontend renamed to `frontend/` (update scripts)

### Next Steps
- [ ] Implement NPC conversation UI (tap NPC to start chat)
- [ ] Generate NPC images using new structured info
- [ ] Add more NPCs to other experience files
- [ ] Test NPC conversations with AI
- [ ] Implement map view UI improvements

---

## Previous Changes
(Add previous changelog entries here)
