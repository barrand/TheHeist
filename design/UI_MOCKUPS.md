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
│  🎭 YOUR ROLE                   │
│  ┌───────────────────────────┐ │
│  │  Mastermind            >  │ │← Tap to change role
│  └───────────────────────────┘ │
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
- [ ] Your role selector (tappable button with visual indicators)
  - [ ] Shows selected role name OR "Select Your Role"
  - [ ] Right chevron icon `>` (indicates opens modal)
  - [ ] Button styling (border/background to show it's tappable)
  - [ ] Tap → Opens Screen 5 (Role Selection Modal)
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

**Role Selector Visual States:**

*When no role selected (needs attention):*
```
│  🎭 YOUR ROLE                   │
│  ┌───────────────────────────┐ │
│  │  Select Your Role      ▼  │ │← Gray text, down chevron
│  └───────────────────────────┘ │
│  Tap to browse all roles        │← Hint text
```

*When role is selected:*
```
│  🎭 YOUR ROLE                   │
│  ┌───────────────────────────┐ │
│  │  Mastermind           ▼   │ │← White text, can change
│  └───────────────────────────┘ │
│  Tap to change role             │← Hint text
```

*Alternative with more explicit button styling:*
```
│  🎭 YOUR ROLE                   │
│  ┌───────────────────────────┐ │
│  │ ⚪ Mastermind         [▼] │ │← Icon + boxed chevron
│  └───────────────────────────┘ │
```

**Actions:**
- Tap scenario → Select it (show required roles)
- Tap role selector button → Opens role selection modal (Screen 5)
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
│  │  Hacker                >  │ │← Tap to change role
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
- [ ] Your role selector (tappable button with visual indicators)
  - [ ] Shows selected role name OR "Select Your Role"
  - [ ] Right chevron icon `>` (indicates opens modal)
  - [ ] Button styling (border/background to show it's tappable)
  - [ ] Tap → Opens Screen 5 (Role Selection Modal)
- [ ] Players list (same as host view)
- [ ] Waiting indicator
- [ ] "Leave Room" link

**Role Selector Visual States:**

*When no role selected (needs attention):*
```
│  🎭 YOUR ROLE                   │
│  ┌───────────────────────────┐ │
│  │  Select Your Role      ▼  │ │← Gray text, down chevron
│  └───────────────────────────┘ │
│  Tap to browse all roles        │← Hint text
```

*When role is selected:*
```
│  🎭 YOUR ROLE                   │
│  ┌───────────────────────────┐ │
│  │  Hacker               ▼   │ │← White text, can change
│  └───────────────────────────┘ │
│  Tap to change role             │← Hint text
```

**Actions:**
- Tap role selector button → Opens role selection modal (Screen 5)
- Player joins/leaves → Update list (real-time)
- Host starts game → Go to Game Screen

---

## 🎯 Design Note: Role Selector Button

**Making it obvious this button opens a modal:**

### Visual Indicators:
1. **Chevron Icon `>`** on the right (universal "tap to open" signal)
2. **Button Styling**: Border + slight background color (not just text)
3. **Interactive State**: Show pressed/hover state when tapped
4. **Hint Text**: When empty, show "Select Your Role" in lighter gray

### Alternative Visual Approaches:
- Add small text below: "Tap to browse roles"
- Use chevron down `▼` instead of right `>`
- Add subtle drop shadow to make it "pop"
- Pulsing animation when no role selected (draw attention)

### iOS/Android Patterns:
- Similar to Settings app rows (Name > chevron → opens detail)
- Similar to contact picker (Select Contact > → opens modal)

---

## Screen 5: Role Selection Modal

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
│  │                           │ │
│  │ Minigames:                │ │
│  │ • pattern_memorization    │ │
│  │ + NPC interactions        │ │
│  │                           │ │
│  │      [Tap for details]    │ │
│  └───────────────────────────┘ │
│                                 │
│  OTHER ROLES                    │
│  ┌───────────────────────────┐ │
│  │ 🚗 Driver          (Taken)│ │← Disabled
│  │ Handles getaway vehicle   │ │
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
  - [ ] Associated minigames list (2-3 shown)
  - [ ] "Tap for details" link (shows full role info modal)
  - [ ] Selected indicator (checkmark + button change)
  - [ ] Disabled state (if taken, grayed out)
- [ ] "Show More" expansion

**Actions:**
- Tap role card → Expand to show selection button
- Tap "Select This Role" → Select it → Close modal, return to Room Lobby
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
- [ ] Minigames section
  - [ ] Each minigame with name and short description
  - [ ] 2-4 minigames shown
- [ ] Role importance indicator (Required/Recommended/Optional)
- [ ] "Select This Role" button (primary CTA)

**Actions:**
- Tap "Select This Role" → Select role → Close modal → Return to lobby
- Tap X → Close modal → Return to role selection

---

## Screen 6: Game Screen

**Purpose**: Main gameplay - show objectives, available tasks, and what you've completed

### UI Elements:

```
┌─────────────────────────────────┐
│ 📍 Vault Room         8/15 ⏱️   │← Location, team progress, timer
│                                 │
│  🎯 TEAM OBJECTIVES             │
│  ┌───────────────────────────┐ │
│  │ 🔓 Get Into the Safe      │ │← High-level goal (tappable)
│  │ 👥 Team task              │ │
│  │ 📍 Vault Room              │ │
│  └───────────────────────────┘ │
│                                 │
│  YOUR TASKS (Safe Cracker)      │
│                                 │
│  ✅ READY TO DO HERE            │
│  ┌───────────────────────────┐ │
│  │ 🔍 Examine the Safe       │ │← Discovery task (tappable)
│  │ ⚡ Tap to start            │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 🎮 Pick Lock on Toolbox   │ │
│  │ lock_picking              │ │
│  │ ⚡ Tap to start            │ │
│  └───────────────────────────┘ │
│                                 │
│  📍 REQUIRES TRAVEL             │
│  ┌───────────────────────────┐ │
│  │ 💬 Ask About Vault Code   │ │← Grayed out (tappable)
│  │ 👥 Team can help          │ │← Team task indicator
│  │ 📍 Curator's Office        │ │
│  │ 👉 Tap to view location   │ │
│  └───────────────────────────┘ │
│                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                 │
│  ✅ COMPLETED (3)         ⌄    │← Expandable
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

**Team Objectives Section:**
- [ ] High-level goals visible to all players
- [ ] "👥 Team task" indicator
- [ ] Shows location if relevant
- [ ] Tappable to see more details
- [ ] May spawn specific tasks upon interaction

**Task List:**
- [ ] Section: "Ready to Do Here" (bright, full color)
  - [ ] Tasks available at current location
  - [ ] Includes discovery tasks (examine, investigate, search)
  - [ ] "⚡ Tap to start" indicator
  - [ ] Fully tappable → Start task immediately
- [ ] Section: "Requires Travel" (grayed out, but visible)
  - [ ] Tasks available but at different locations
  - [ ] Shows "👥 Team can help" for team tasks
  - [ ] Location name shown prominently
  - [ ] "👉 Tap to view location" indicator
  - [ ] Tappable → Shows map with location highlighted
- [ ] Each task card shows:
  - [ ] Task icon (🎮 minigame, 💬 NPC, 🔍 search, 🤝 handoff, 🗣️ info)
  - [ ] Task name
  - [ ] Team task indicator (if applicable)
  - [ ] Minigame ID (if applicable, for "Ready" tasks)
  - [ ] Location name (for "Travel" tasks)
- [ ] Divider line
- [ ] Completed section (collapsed, shows count)

**Bottom Navigation:**
- [ ] "Map" button → Location view
- [ ] "Team" button → Team status view

**Design Notes - Discovery System:**
- **Objectives** are high-level goals shown upfront (e.g., "Get Into the Safe")
- **Discovery tasks** appear when players examine/investigate (e.g., "Examine the Safe")
- **Triggered tasks** spawn after discovery (e.g., after examining safe → "Find Combination" appears for team)
- **Team tasks** visible to multiple/all players (marked with 👥)
- **Player-specific tasks** only visible to assigned player
- Only show currently available tasks (no locked/upcoming tasks visible)
- New tasks appear dynamically based on:
  - Dependencies being met
  - Discovery moments (examining objects, talking to NPCs)
  - Team member actions (someone finds a clue → new task for another player)
- Location-blocked tasks are visible but visually distinct (grayed)

**Example Discovery Flow:**
1. Objective shown: "🔓 Get Into the Safe" (team)
2. Safe Cracker sees: "🔍 Examine the Safe" (at safe location)
3. After examining → New tasks appear:
   - "Find Combination" (team task, anyone can do)
   - "Crack Safe" (Safe Cracker only, needs combination first)
4. Team discovers combination → "Crack Safe" becomes available

**Actions:**
- Tap objective → See details and which players are working on related tasks
- Tap "Ready" task → Start task immediately (minigame/NPC/search/discovery)
- Tap "Travel" task → Open map view with that location highlighted
- Tap "Completed" → Expand to show completed tasks
- Tap "Map" → Show location map and available locations
- Tap "Team" → Show all players and their current tasks

---

## Screen 6b: Team Objective Detail Modal

**Purpose**: Show team objective status and who's working on it

### UI Elements:

```
┌─────────────────────────────────┐
│  🔓 GET INTO THE SAFE       ✕   │
│                                 │
│  TEAM OBJECTIVE                 │
│  📍 Location: Vault Room        │
│                                 │
│  Status: In Progress            │
│                                 │
│  TEAM MEMBERS WORKING:          │
│  ┌───────────────────────────┐ │
│  │ 👤 You (Safe Cracker)     │ │
│  │ 🔍 Examining the safe     │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 👤 Alex (Insider)         │ │
│  │ 💬 Asking curator about   │ │
│  │    vault code             │ │
│  └───────────────────────────┘ │
│                                 │
│  RELATED TASKS:                 │
│  • 🔍 Examine the Safe (You)   │
│  • 💬 Ask About Vault Code     │
│  • 🔍 Find Combination (TBD)   │
│                                 │
│        Close                    │
└─────────────────────────────────┘
```

**Components:**
- [ ] Objective title (large)
- [ ] Objective type (Team/Role-specific)
- [ ] Location (if applicable)
- [ ] Status indicator
- [ ] Team members working on related tasks
  - [ ] Player name and role
  - [ ] Current task related to objective
- [ ] Related tasks list
  - [ ] Shows discovered and undiscovered tasks
  - [ ] "TBD" for tasks that will appear after discovery
- [ ] Close button

**Actions:**
- Shows coordination - who's doing what
- Tap Close → Return to game screen

---

## Screen 7a: Task Detail Modal - Current Location

**Purpose**: Show task details before starting (when at correct location)

### UI Elements:

```
┌─────────────────────────────────┐
│  PREP HACKING DEVICE            │
│                                 │
│  🎮 Minigame: wire_connecting   │
│  📍 Location: Safe House ✓      │
│                                 │
│  Description:                   │
│  Assemble USB device in van,    │
│  connect wires correctly to     │
│  prepare the hacking tool.      │
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
- [ ] Location requirement (with checkmark if at location)
- [ ] Description (from generated experience)
- [ ] "Start Task" button (enabled)
- [ ] "Cancel" link

---

## Screen 7b: Task Detail Modal - Wrong Location

**Purpose**: Show task details when player needs to travel

### UI Elements:

```
┌─────────────────────────────────┐
│  TALK TO SECURITY GUARD         │
│                                 │
│  💬 NPC Conversation            │
│  📍 Location: Museum Front Steps│
│                                 │
│  Description:                   │
│  Approach the guard at the      │
│  front entrance and convince    │
│  him you're a VIP guest.        │
│                                 │
│  ⚠️ You must travel to this     │
│     location first              │
│                                 │
│  ┌───────────────────────────┐ │
│  │   📍 VIEW ON MAP          │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🚶 TRAVEL THERE         │ │
│  └───────────────────────────┘ │
│                                 │
│        Cancel                   │
└─────────────────────────────────┘
```

**Components:**
- [ ] Task title
- [ ] Task type icon
- [ ] Location requirement (highlighted)
- [ ] Description (from generated experience)
- [ ] Warning message (not at correct location)
- [ ] "View on Map" button
- [ ] "Travel There" button (moves player to that location)
- [ ] "Cancel" link

**Design Notes:**
- No dependencies shown (if task is available, dependencies are already met)
- Keeps mystery while providing context for the task
- Clear indication when player needs to move

**Actions:**
- **Current Location:** Tap "Start Task" → Launch minigame/NPC/search screen
- **Wrong Location:** Tap "Travel There" → Move to location → Return to game screen
- **Wrong Location:** Tap "View on Map" → Open map with location highlighted
- Tap "Cancel" → Return to game screen

---

## Screen 7c: Discovery Result Screen

**Purpose**: Show what was discovered and new tasks that appeared

### UI Elements:

```
┌─────────────────────────────────┐
│         🔍 DISCOVERY!           │
│                                 │
│  You examined the safe and      │
│  found:                         │
│                                 │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │   🔐                      │ │
│  │                           │ │
│  │ "This is a Vanderbilt     │ │
│  │  Model 3200. It requires  │ │
│  │  a 6-digit combination."  │ │
│  │                           │ │
│  └───────────────────────────┘ │
│                                 │
│  ✨ NEW TASKS UNLOCKED          │
│                                 │
│  FOR YOUR TEAM:                 │
│  • 💬 Find Vault Combination   │
│    (Anyone can do this)         │
│                                 │
│  FOR YOU:                       │
│  • 🎮 Crack Safe (Locked)      │
│    Needs: Combination          │
│                                 │
│  ┌───────────────────────────┐ │
│  │   CONTINUE                │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Discovery title with animation
- [ ] Discovery description/flavor text
- [ ] What was discovered (visual + text)
- [ ] "New Tasks Unlocked" section
- [ ] Team tasks list (marked as team)
- [ ] Personal tasks list (your role)
- [ ] Shows if new tasks are available or locked
- [ ] Continue button

**Design Notes:**
- Appears after completing discovery tasks (examine, search, investigate)
- Shows immediate impact of discovery
- Announces new tasks to player
- Team gets notification that new tasks available
- Creates "aha!" moments

**Actions:**
- Tap Continue → Return to game screen with new tasks visible
- Team members get real-time notification of new tasks

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
4. ✅ Role Selection Modal (with minigame info)
5. ✅ Role Detail Modal
6. ✅ Game Screen (with objectives & discovery)
7. ✅ Team Objective Detail Modal
8. ✅ Task Detail Modal (current location)
9. ✅ Task Detail Modal (wrong location)
10. ✅ Discovery Result Screen

**Phase 2 (Should Have):**
11. ✅ Team View
12. ✅ NPC Conversation
13. ✅ Search Screen

**Phase 3 (Nice to Have):**
14. ✅ Map View
15. ✅ Minigame Screens (build 2-3)
16. ✅ Victory Screen

---

## 🚀 Next Steps

1. Review these mockups
2. Create high-fidelity designs (Figma optional)
3. Start Flutter project
4. Build screens in priority order
5. Connect to WebSocket backend

