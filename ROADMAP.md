# The Heist - Development Roadmap

## ✅ Completed

### Phase 0: Foundation & Design
- [x] Document project concept and game pillars
- [x] Create role taxonomy (12 roles with minigames)
- [x] Create scenario taxonomy (11 heist scenarios)
- [x] Design dependency tree system
- [x] Create NPC personality guide
- [x] Build example dependency trees (museum gala, train robbery)
- [x] Set up Gemini AI integration
- [x] Build experience generator script (`generate_experience.py`)
- [x] Test generation with 4 and 6 player scenarios

---

## 🚧 Current Phase: Multiplayer Foundation

### Phase 1: Player Experience Flow
- [ ] **Landing Page**
  - [ ] Create room UI (generate room code)
  - [ ] Join room UI (enter code)
  - [ ] Room code generation logic
  
- [ ] **Multiplayer Connection**
  - [ ] Set up WebSocket server (real-time communication)
  - [ ] Room management (create, join, leave)
  - [ ] Player state synchronization
  - [ ] Host designation (first player is host)
  
- [ ] **Room Lobby**
  - [ ] Display room code prominently
  - [ ] Show connected players list
  - [ ] Role selection UI (each player picks role)
  - [ ] Scenario selection UI (host only)
  - [ ] Player count validation (3-12 players)
  - [ ] Start game button (host only, enabled when ready)
  
- [ ] **Experience Generation Integration**
  - [ ] Call `generate_experience.py` when host starts game
  - [ ] Parse generated markdown into JSON structure
  - [ ] Distribute tasks to each player based on role
  - [ ] Store experience state in database/memory
  
- [ ] **Game Screen (Basic)**
  - [ ] Display player's current location
  - [ ] Show player's task list
  - [ ] Simple checkbox task completion (temporary, replace with minigames later)
  - [ ] Show dependencies (locked tasks vs available tasks)
  - [ ] Real-time sync when teammates complete tasks
  
- [ ] **Technology Stack Decision**
  - [x] Frontend: Dart/Flutter (mobile web + future app)
  - [ ] Backend: Python (WebSocket server, experience generation)
  - [ ] Database: TBD (PostgreSQL, Firebase, or similar)
  - [ ] Hosting: TBD (Heroku, AWS, Google Cloud)

---

## 📅 Future Phases

### Phase 2: Minigame System
- [ ] Build minigame framework
- [ ] Implement 3-5 simple minigames
  - [ ] `fuel_pump` - Hold button to fill tank
  - [ ] `timing_tap` - Tap at right moment
  - [ ] `button_mash_barrier` - Rapid tapping
  - [ ] `wire_connecting` - Connect matching wires
  - [ ] `dial_rotation` - Rotate dial to combination
- [ ] Touch controls for mobile
- [ ] Success/failure states
- [ ] Replace checkboxes with minigame triggers

### Phase 3: NPC Conversation System
- [ ] Build chat interface
- [ ] Integrate Gemini Flash Lite for real-time NPC responses
- [ ] Load NPC personality from experience file
- [ ] Dialogue choice system
- [ ] Success/failure based on personality reading
- [ ] Track conversation outcomes

### Phase 4: Room Inventory & Search
- [ ] Implement 🔍 Search mechanic
- [ ] Room inventory system
- [ ] Item discovery UI
- [ ] Item handoff system between players

### Phase 5: Location & Movement
- [ ] Build location/room map
- [ ] Movement between locations
- [ ] Location-based task availability
- [ ] Visual map representation

### Phase 6: Game State Dashboard (Optional Main Screen)
- [ ] Team progress overview
- [ ] Timeline visualization
- [ ] Live player locations
- [ ] Task completion tracking
- [ ] Optional TV/projection mode

### Phase 7: Payment & Monetization
- [ ] Convert to native mobile app (Flutter compiles to iOS/Android)
- [ ] Integrate payment system (Stripe, in-app purchases)
- [ ] Free first heist, paid scenarios
- [ ] Campaign mode unlocks

### Phase 8: Polish & Features
- [ ] Sound effects and music
- [ ] Animations and transitions
- [ ] Tutorial/onboarding
- [ ] Player profiles and stats
- [ ] Replay system
- [ ] Social features (invite friends, leaderboards)

### Phase 9: Content Expansion
- [ ] Add more scenarios (target: 30-50 scenarios)
- [ ] New chapters (pirate crew, space team, etc.)
- [ ] New roles and specialties
- [ ] Seasonal/themed heists
- [ ] Community-created scenarios (stretch goal)

### Phase 10: Advanced Features
- [ ] Voice chat integration
- [ ] AI-generated images for NPCs
- [ ] Text-to-speech for NPC dialogue
- [ ] Video clips for story moments
- [ ] Dynamic difficulty adjustment
- [ ] Procedural scenario generation

---

## 🎯 Success Metrics

### MVP (Minimum Viable Product)
- 2-3 playable scenarios
- 5-10 minigames working
- 3-12 players can connect and complete a heist
- NPC conversations functional
- Mobile web works smoothly

### Launch Targets
- 10+ scenarios across 2 chapters
- All 12 roles implemented
- Smooth multiplayer experience
- Payment system working
- 4.5+ star rating

---

## 🛠️ Technical Decisions

### Why Dart/Flutter?
✅ **Perfect for your use case:**
- Single codebase → mobile web NOW, native apps LATER
- Excellent performance for minigames (60fps animations)
- Built-in touch controls and gestures
- Hot reload for fast development
- Compiles to iOS, Android, Web from same code
- Good for payments (Flutter has Stripe integration)

### Why WebSockets for Multiplayer?
✅ **Best for real-time games:**
- Instant updates when tasks complete
- Low latency (important for coordination)
- Persistent connection (players stay synced)
- Industry standard for multiplayer games

### Backend Options
**Recommended: Python + FastAPI + WebSockets**
- You already have Python experience generator
- FastAPI handles WebSockets natively
- Can integrate with your existing scripts
- Easy to deploy

---

## 📝 Notes

- Start with mobile web to iterate fast
- Convert to native app only when ready for payments
- Use Flutter's responsive design for desktop web too
- Keep backend simple initially (in-memory state, add DB later)
- Focus on fun gameplay before monetization
