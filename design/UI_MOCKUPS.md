# The Heist - UI Mockups & Screen Flow

## 🎨 Design Principles

- **Mobile-First**: All screens designed for mobile web (portrait orientation)
- **Dark Theme**: Heist/noir aesthetic (black/dark gray background, white/gold text)
- **Large Touch Targets**: Minimum 44x44pt for buttons (accessibility)
- **Simple Navigation**: No more than 2 taps to any action
- **Real-Time Updates**: Show live changes when teammates act

---

## 📱 Screen Flow Overview

```
Landing Page
    ↓
    ├─→ Create Room → Room Lobby (Host)
    └─→ Join Room → Room Lobby (Player)
             ↓
        (Host starts game)
             ↓
         Game Screen
             ↓
        Victory Screen
```

---

## Screen 1: Landing Page

**Purpose**: First screen - choose to host or join a game

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│         THE HEIST 🎭            │
│    Collaborative Heist Game     │
│                                 │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │   🎮 CREATE ROOM          │ │
│  │                           │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │   🔑 JOIN ROOM            │ │
│  │                           │ │
│  └───────────────────────────┘ │
│                                 │
│                                 │
│        How to Play ℹ️           │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] App title/logo (centered)
- [ ] Tagline text
- [ ] "Create Room" button (primary CTA)
- [ ] "Join Room" button (secondary CTA)
- [ ] "How to Play" link (bottom)
- [ ] Version number (tiny, bottom corner)

**Actions:**
- Tap "Create Room" → Go to Room Lobby (as Host)
- Tap "Join Room" → Show "Enter Code" modal → Go to Room Lobby (as Player)
- Tap "How to Play" → Show tutorial/info modal

---

## Screen 2: Join Room Modal

**Purpose**: Enter room code to join existing game

### UI Elements:

```
┌─────────────────────────────────┐
│  Enter Room Code                │
│                                 │
│  ┌─────────────────────────┐   │
│  │                         │   │
│  │   [  4  S  2  X  ]      │   │  ← Large input
│  │                         │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌──────────────┐              │
│  │   JOIN   ✓   │              │
│  └──────────────┘              │
│                                 │
│        Cancel                   │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Modal overlay (dims background)
- [ ] Title "Enter Room Code"
- [ ] 4-character code input (large, auto-caps)
- [ ] "Join" button (disabled until 4 chars entered)
- [ ] "Cancel" link
- [ ] Error message area (if invalid code)

**Actions:**
- Enter 4 characters → Enable "Join" button
- Tap "Join" → Validate code → Go to Room Lobby
- Tap "Cancel" → Return to Landing Page

---

## Screen 3: Room Lobby (Host View)

**Purpose**: Wait for players, select scenario/roles, start game

### UI Elements:

```
┌─────────────────────────────────┐
│  Room Code: 4S2X           📋   │← Copy button
│  (3 of 12 players)              │
│                                 │
│  🎭 SCENARIO SELECTION          │
│  ┌───────────────────────────┐ │
│  │ Museum Gala Vault Heist   │ │← Selected
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ Armored Train Robbery     │ │
│  └───────────────────────────┘ │
│  [Show More...]                 │
│                                 │
│  👥 PLAYERS                     │
│  ┌───────────────────────────┐ │
│  │ 👑 You - Mastermind ✓     │ │← Host (crown)
│  │ 👤 Alex - Hacker ✓        │ │
│  │ 👤 Sam - Safe Cracker ✓   │ │
│  └───────────────────────────┘ │
│                                 │
│  ⚠️ Need 1-9 more players       │
│                                 │
│  ┌───────────────────────────┐ │
│  │   START HEIST 🚀          │ │← Disabled (not ready)
│  └───────────────────────────┘ │
│                                 │
│        Leave Room               │
└─────────────────────────────────┘
```

**Components:**
- [ ] Room code display (large, prominent)
- [ ] Copy room code button
- [ ] Player count indicator
- [ ] Scenario selection list/dropdown
  - [ ] Show scenario name
  - [ ] Show required roles
  - [ ] Visual checkmark when selected
- [ ] Players list
  - [ ] Host indicator (crown icon)
  - [ ] Player name
  - [ ] Selected role
  - [ ] Checkmark when role selected
  - [ ] Empty slots (gray placeholders)
- [ ] Ready state indicator
- [ ] "Start Heist" button (disabled until ready)
- [ ] "Leave Room" link (bottom)

**Ready State Rules:**
- ✓ Scenario selected
- ✓ All players have roles
- ✓ 3-12 players
- ✓ Required roles for scenario are covered

**Actions:**
- Tap scenario → Select it (show required roles)
- Tap role dropdown → Select your role
- Player joins → Add to list (real-time)
- Player leaves → Remove from list (real-time)
- Tap "Start Heist" → Generate experience → Go to Game Screen

---

## Screen 4: Room Lobby (Player View)

**Purpose**: Wait for host to start, select your role

### UI Elements:

```
┌─────────────────────────────────┐
│  Room Code: 4S2X           📋   │
│  (3 of 12 players)              │
│                                 │
│  🎭 SCENARIO                    │
│  Museum Gala Vault Heist        │← Read-only
│  Required: Mastermind, Insider, │
│            Safe Cracker          │
│                                 │
│  🎭 YOUR ROLE                   │
│  ┌───────────────────────────┐ │
│  │ Hacker              ✓     │ │← Dropdown
│  └───────────────────────────┘ │
│                                 │
│  👥 PLAYERS                     │
│  ┌───────────────────────────┐ │
│  │ 👑 Brian - Mastermind ✓   │ │← Host
│  │ 👤 You - Hacker ✓         │ │← You
│  │ 👤 Sam - Safe Cracker ✓   │ │
│  └───────────────────────────┘ │
│                                 │
│  ⏳ Waiting for host to start...│
│                                 │
│        Leave Room               │
└─────────────────────────────────┘
```

**Components:**
- [ ] Room code display (read-only)
- [ ] Player count indicator
- [ ] Scenario name (read-only, set by host)
- [ ] Required roles list
- [ ] Your role selector (dropdown)
  - [ ] Show all available roles
  - [ ] Gray out roles already taken
  - [ ] Highlight recommended roles
- [ ] Players list (same as host view)
- [ ] Waiting indicator
- [ ] "Leave Room" link

**Actions:**
- Tap role dropdown → Select role
- Player joins/leaves → Update list (real-time)
- Host starts game → Go to Game Screen

---

## Screen 5: Role Selection Dropdown

**Purpose**: Choose your role from available options

### UI Elements:

```
┌─────────────────────────────────┐
│  SELECT YOUR ROLE               │
│                                 │
│  REQUIRED (choose one)          │
│  ┌───────────────────────────┐ │
│  │ ⭐ Mastermind             │ │
│  │ Coordinates team actions  │ │
│  │ 📋 3-4 tasks expected     │ │
│  │                           │ │
│  │ Minigames:                │ │
│  │ • pattern_memorization    │ │
│  │ • time_allocation         │ │
│  │                           │ │
│  │      [Tap for details]    │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 🔓 Safe Cracker           │ │
│  │ Opens vaults and safes    │ │
│  │ 📋 4-5 tasks expected     │ │
│  │                           │ │
│  │ Minigames:                │ │
│  │ • safe_crack_rotation     │ │
│  │ • lock_picking            │ │
│  │                           │ │
│  │      [Tap for details]    │ │
│  └───────────────────────────┘ │
│                                 │
│  RECOMMENDED                    │
│  ┌───────────────────────────┐ │
│  │ 💻 Hacker          ✓      │ │← Selected
│  │ Disables security systems │ │
│  │ 📋 5-6 tasks expected     │ │
│  │                           │ │
│  │ Minigames:                │ │
│  │ • wire_connecting         │ │
│  │ • cipher_wheel_alignment  │ │
│  │ • match_ip_addresses      │ │
│  │                           │ │
│  │   [SELECT THIS ROLE] ✓    │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 👔 Insider                │ │
│  │ Knows building layout     │ │
│  │ 📋 3-4 tasks expected     │ │
│  │                           │ │
│  │ Minigames:                │ │
│  │ • pattern_memorization    │ │
│  │ Many NPC interactions     │ │
│  │                           │ │
│  │      [Tap for details]    │ │
│  └───────────────────────────┘ │
│                                 │
│  OTHER ROLES                    │
│  ┌───────────────────────────┐ │
│  │ 🚗 Driver          (Taken)│ │← Disabled
│  │ Handles getaway vehicle   │ │
│  │ 📋 4-5 tasks expected     │ │
│  └───────────────────────────┘ │
│                                 │
│  [Show More Roles...]           │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Role categories
  - [ ] Required (for this scenario)
  - [ ] Recommended
  - [ ] Other roles
- [ ] Role cards (expanded)
  - [ ] Role icon
  - [ ] Role name
  - [ ] Extended description (2-3 words)
  - [ ] Expected task count
  - [ ] Associated minigames list (2-3 shown)
  - [ ] "Tap for details" link (shows full role info modal)
  - [ ] Selected indicator (checkmark + button change)
  - [ ] Disabled state (if taken, grayed out)
- [ ] "Show More" expansion

**Actions:**
- Tap role card → Expand to show selection button
- Tap "Select This Role" → Select it → Close dropdown
- Tap "Tap for details" → Show Role Detail Modal (see below)
- Scroll to see all roles

---

## Screen 5b: Role Detail Modal

**Purpose**: Show comprehensive role information before selecting

### UI Elements:

```
┌─────────────────────────────────┐
│  💻 HACKER                  ✕   │
│                                 │
│  DESCRIPTION                    │
│  Tech specialist who disables   │
│  security systems, hacks        │
│  cameras, and provides digital  │
│  access to restricted areas.    │
│                                 │
│  RESPONSIBILITIES               │
│  • Disable security cameras     │
│  • Hack electronic locks        │
│  • Monitor security feeds       │
│  • Coordinate with team via     │
│    encrypted channels           │
│                                 │
│  EXPECTED TASKS: 5-6            │
│                                 │
│  MINIGAMES YOU'LL PLAY          │
│  ┌───────────────────────────┐ │
│  │ 🎮 Wire Connecting        │ │
│  │ Match colored wires       │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 🎮 Cipher Wheel Alignment │ │
│  │ Align symbols to decrypt  │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 🎮 IP Address Matching    │ │
│  │ Match network addresses   │ │
│  └───────────────────────────┘ │
│                                 │
│  INTERACTIONS                   │
│  • 💬 NPCs (2-3 conversations) │
│  • 🤝 Team handoffs (2-3)      │
│  • 🔍 Search tasks (1-2)       │
│                                 │
│  ⚠️ This role is RECOMMENDED   │
│     for this scenario           │
│                                 │
│  ┌───────────────────────────┐ │
│  │   SELECT THIS ROLE ✓      │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Close button (X)
- [ ] Role icon and name (large)
- [ ] Full description paragraph
- [ ] Responsibilities list
- [ ] Expected task count
- [ ] Minigames section
  - [ ] Each minigame with name and short description
  - [ ] 2-4 minigames shown
- [ ] Interactions summary
  - [ ] NPC conversation count
  - [ ] Team handoff count
  - [ ] Search task count
- [ ] Role importance indicator (Required/Recommended/Optional)
- [ ] "Select This Role" button (primary CTA)

**Actions:**
- Tap "Select This Role" → Select role → Close modal → Return to lobby
- Tap X → Close modal → Return to role selection

---

## Screen 6: Game Screen

**Purpose**: Main gameplay - show tasks, location, dependencies

### UI Elements:

```
┌─────────────────────────────────┐
│ 📍 Safe House         3/12 ⏱️   │← Location, team progress, timer
│                                 │
│  YOUR TASKS (Hacker)            │
│                                 │
│  🟢 AVAILABLE                   │
│  ┌───────────────────────────┐ │
│  │ 🎮 Prep Hacking Device    │ │← Tap to start
│  │ wire_connecting           │ │
│  │ 📍 Safe House              │ │
│  └───────────────────────────┘ │
│                                 │
│  🔒 LOCKED                      │
│  ┌───────────────────────────┐ │
│  │ 🎮 Disable Cameras        │ │
│  │ cipher_wheel_alignment    │ │
│  │ 📍 Security Room           │ │
│  │ ⚠️ Needs: Device planted   │ │← Dependency
│  └───────────────────────────┘ │
│                                 │
│  ✅ COMPLETED                   │
│  ┌───────────────────────────┐ │
│  │ 🔍 Find Ethernet Cable    │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────┐ ┌─────────┐│
│  │ 🗺️ Map       │ │ 👥 Team │││← Quick actions
│  └───────────────┘ └─────────┘││
└─────────────────────────────────┘
```

**Components:**

**Top Bar:**
- [ ] Current location icon + name
- [ ] Team progress (X/Y tasks done)
- [ ] Timer (optional)

**Task List:**
- [ ] Section: Available (green)
  - [ ] Task cards (tappable)
  - [ ] Task icon (🎮 minigame, 💬 NPC, 🔍 search, 🤝 handoff, 🗣️ info)
  - [ ] Task name
  - [ ] Minigame ID (if applicable)
  - [ ] Location
- [ ] Section: Locked (gray)
  - [ ] Task cards (not tappable)
  - [ ] Show dependencies
  - [ ] Lock icon
- [ ] Section: Completed (collapsed, expandable)
  - [ ] Checkmark icon
  - [ ] Grayed out

**Bottom Navigation:**
- [ ] "Map" button → Location view
- [ ] "Team" button → Team status view

**Actions:**
- Tap available task → Start task (minigame/NPC/search)
- Tap locked task → Show dependencies
- Tap "Map" → Show location map and available locations
- Tap "Team" → Show all players and their current tasks

---

## Screen 7: Task Detail Modal (Before Starting)

**Purpose**: Show task details before starting

### UI Elements:

```
┌─────────────────────────────────┐
│  PREP HACKING DEVICE            │
│                                 │
│  🎮 Minigame: wire_connecting   │
│  📍 Location: Safe House        │
│                                 │
│  Description:                   │
│  Assemble USB device in van,    │
│  connect wires correctly        │
│                                 │
│  Dependencies:                  │
│  ✅ Found Ethernet Cable        │
│                                 │
│  ┌───────────────────────────┐ │
│  │   START TASK 🎮           │ │
│  └───────────────────────────┘ │
│                                 │
│        Cancel                   │
└─────────────────────────────────┘
```

**Components:**
- [ ] Task title
- [ ] Task type icon
- [ ] Location
- [ ] Description (from generated experience)
- [ ] Dependencies list with status
- [ ] "Start Task" button
- [ ] "Cancel" link

**Actions:**
- Tap "Start Task" → Launch minigame/NPC/search screen
- Tap "Cancel" → Return to game screen

---

## Screen 8: Map View

**Purpose**: Show all locations and movement options

### UI Elements:

```
┌─────────────────────────────────┐
│  LOCATIONS                  ✕   │
│                                 │
│  CURRENT                        │
│  ┌───────────────────────────┐ │
│  │ 📍 Safe House       ⭐    │ │← You are here
│  └───────────────────────────┘ │
│                                 │
│  ACCESSIBLE                     │
│  ┌───────────────────────────┐ │
│  │ 🏛️ Museum Front Steps     │ │← Can move here
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 🚗 Getaway Vehicle        │ │
│  └───────────────────────────┘ │
│                                 │
│  LOCKED                         │
│  ┌───────────────────────────┐ │
│  │ 🔒 Security Room          │ │← Can't access yet
│  │    Needs: Badge access    │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Close button (X)
- [ ] Current location (highlighted)
- [ ] Accessible locations (tappable)
- [ ] Locked locations (grayed out)
  - [ ] Show unlock requirement
- [ ] Location icons
- [ ] Location names

**Actions:**
- Tap accessible location → Move there (update current location)
- Tap locked location → Show why it's locked
- Tap X → Close modal

---

## Screen 9: Team View

**Purpose**: See what all players are doing

### UI Elements:

```
┌─────────────────────────────────┐
│  TEAM STATUS                ✕   │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 👤 You (Hacker)           │ │
│  │ 📍 Safe House              │ │
│  │ 🎮 Prep Hacking Device    │ │← Current task
│  │ ● In Progress             │ │← Status
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 👑 Brian (Mastermind)     │ │
│  │ 📍 Safe House              │ │
│  │ 💬 Briefing Crew          │ │
│  │ ✓ Completed               │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 👤 Sam (Safe Cracker)     │ │
│  │ 📍 Museum Entrance         │ │
│  │ 🔍 Looking for tools      │ │
│  │ ● In Progress             │ │
│  └───────────────────────────┘ │
│                                 │
│  Team Progress: 8/45 tasks     │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Close button (X)
- [ ] Player cards
  - [ ] Player name and role
  - [ ] Crown if host
  - [ ] Current location
  - [ ] Current task (if any)
  - [ ] Status indicator (idle, in progress, completed)
- [ ] Team progress bar
- [ ] Task completion count

**Actions:**
- Real-time updates when players complete tasks
- Tap X → Close modal

---

## Screen 10: NPC Conversation Screen

**Purpose**: Chat with an NPC character

### UI Elements:

```
┌─────────────────────────────────┐
│  < Back                         │
│                                 │
│         CARLOS                  │
│    (suspicious, greedy)         │
│                                 │
│  ┌───────────────────────────┐ │
│  │ "Uniform? Yeah I got it.  │ │← NPC message
│  │  But prices went up.       │ │
│  │  Security's been tight.    │ │
│  │  I need $200 more."        │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ [You]: Here's the cash    │ │← Your previous response
│  └───────────────────────────┘ │
│                                 │
│  CHOOSE YOUR RESPONSE:          │
│  ┌───────────────────────────┐ │
│  │ A) Negotiate price down   │ │← Dialogue options
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ B) Pay the extra $200     │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ C) Threaten him           │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Back button
- [ ] NPC name
- [ ] NPC personality traits
- [ ] Chat history
  - [ ] NPC messages (left-aligned)
  - [ ] Your messages (right-aligned)
- [ ] Response options (3-4 buttons)
- [ ] Success/failure indicator (after response)

**Actions:**
- Tap response option → Send to LLM → Get NPC reaction
- Success → Task complete, unlock next task
- Failure → Retry or alternative path

---

## Screen 11: Search/Hunt Screen

**Purpose**: Search a location for items

### UI Elements:

```
┌─────────────────────────────────┐
│  < Back                         │
│                                 │
│  🔍 SEARCHING                   │
│  Safe House                     │
│                                 │
│  Looking for: Ethernet Cable    │
│                                 │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │   🗄️  📦  🛋️  🚪        │ │← Interactive items
│  │                           │ │
│  │   🧰  📺  🪑  🗃️        │ │
│  │                           │ │
│  └───────────────────────────┘ │
│                                 │
│  Tap items to search...         │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Back button
- [ ] Location name
- [ ] What you're looking for
- [ ] Interactive area with items to tap
- [ ] Instruction text

**Actions:**
- Tap wrong items → "Not here" feedback
- Tap correct item → Success animation → Item found
- Found item → Complete task → Return to game screen

---

## Screen 12: Minigame Screen (Example: wire_connecting)

**Purpose**: Interactive minigame

### UI Elements:

```
┌─────────────────────────────────┐
│  < Quit                         │
│                                 │
│  PREP HACKING DEVICE            │
│  Connect matching wires         │
│                                 │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │  🔴─────╮                 │ │
│  │         │                 │ │
│  │  🟢─────┼────────╮        │ │
│  │         │        │        │ │
│  │  🔵─────┴────╮   │        │ │
│  │              │   │        │ │
│  │  ⚪─────────╰───┴───╮    │ │
│  │                      │    │ │
│  │              ◯  ◯  ◯  ◯  │ │← Drag to connect
│  │                           │ │
│  └───────────────────────────┘ │
│                                 │
│  Time: 0:45                     │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Quit button (confirm before quitting)
- [ ] Task name
- [ ] Instructions
- [ ] Game canvas/area
- [ ] Timer (if applicable)
- [ ] Progress indicator

**Actions:**
- Complete minigame → Success screen → Return to game screen
- Fail minigame → Failure screen → Retry or return
- Tap Quit → Confirm modal → Return to game screen

---

## Screen 13: Victory Screen

**Purpose**: Celebrate successful heist

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│         🎉 SUCCESS! 🎉          │
│                                 │
│     Heist Completed!            │
│                                 │
│  Time: 23:15                    │
│  Tasks Completed: 45/45         │
│                                 │
│  ⭐⭐⭐                          │← Star rating
│                                 │
│  MVP: Sam (Safe Cracker)        │
│  (12 tasks completed)           │
│                                 │
│  ┌───────────────────────────┐ │
│  │   PLAY AGAIN              │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │   TRY NEW SCENARIO        │ │
│  └───────────────────────────┘ │
│                                 │
│        Back to Menu             │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Success message with animation
- [ ] Stats
  - [ ] Time taken
  - [ ] Tasks completed
  - [ ] Star rating (3 stars = perfect)
- [ ] MVP (most tasks completed)
- [ ] "Play Again" button (same scenario/roles)
- [ ] "Try New Scenario" button
- [ ] "Back to Menu" link

**Actions:**
- Tap "Play Again" → Generate new experience, go to game screen
- Tap "Try New Scenario" → Return to room lobby
- Tap "Back to Menu" → Return to landing page

---

## 🎨 Design Tokens (Colors & Styling)

### Color Palette:
```
Background:    #0F0F0F (almost black)
Surface:       #1E1E1E (dark gray cards)
Primary:       #D4AF37 (gold - for CTAs)
Secondary:     #8B7355 (bronze)
Success:       #4CAF50 (green)
Error:         #F44336 (red)
Warning:       #FFC107 (amber)
Text Primary:  #FFFFFF (white)
Text Secondary:#B0B0B0 (gray)
Disabled:      #555555 (dark gray)
```

### Typography:
```
Heading 1:     32px, Bold
Heading 2:     24px, SemiBold
Heading 3:     18px, SemiBold
Body:          16px, Regular
Caption:       14px, Regular
Button:        16px, SemiBold
```

### Spacing:
```
Padding (screen edges): 16px
Card padding:           16px
Button height:          48px
Card border radius:     12px
Button border radius:   8px
Icon size:              24px
```

---

## 🔄 Real-Time Updates

**What updates in real-time:**
- Player joins/leaves room
- Player selects/changes role
- Player completes a task
- Player changes location
- Host selects scenario
- Host starts game

**Implementation:**
- WebSocket connection from Flutter app
- Server broadcasts changes to all clients in room
- UI re-renders automatically

---

## 📱 Responsive Considerations

**Mobile (Primary Target):**
- Portrait orientation
- Single column layout
- Large touch targets (44x44pt minimum)
- Bottom navigation for thumbs

**Tablet:**
- Can show side-by-side views (map + tasks)
- Larger text and spacing

**Desktop (Bonus):**
- Max width: 480px (mobile-like)
- Centered on screen
- Or multi-column layout for "main screen" view

---

## 🎯 Priority Screens for MVP

**Phase 1 (Must Have):**
1. ✅ Landing Page
2. ✅ Join Room Modal
3. ✅ Room Lobby (Host & Player views)
4. ✅ Role Selection Dropdown (with minigame info)
5. ✅ Role Detail Modal
6. ✅ Game Screen
7. ✅ Task Detail Modal

**Phase 2 (Should Have):**
8. ✅ Team View
9. ✅ NPC Conversation
10. ✅ Search Screen

**Phase 3 (Nice to Have):**
11. ✅ Map View
12. ✅ Minigame Screens (build 2-3)
13. ✅ Victory Screen

---

## 🚀 Next Steps

1. Review these mockups
2. Create high-fidelity designs (Figma optional)
3. Start Flutter project
4. Build screens in priority order
5. Connect to WebSocket backend

