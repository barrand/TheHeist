# The Crew - Chapter 1: Heist - UI Mockups & Screen Flow

> 💡 **For detailed design specs (colors, typography, spacing, components), see:** [`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md)

## 🎨 Design Principles

- **Mobile-First**: All screens designed for mobile web (portrait orientation)
- **Dark Theme**: Heist/noir aesthetic (black #0F0F0F background, white/gold #D4AF37 text)
- **Large Touch Targets**: Minimum 44x44pt for buttons (accessibility)
- **Simple Navigation**: No more than 2 taps to any action
- **Real-Time Updates**: Show live changes when teammates act
- **Borderlands Art Style**: Character portraits (2D, cell-shaded, comic book)

**Quick Color Reference:**
- Background: `#0F0F0F` (deep black), `#1E1E1E` (cards)
- Accent/Gold: `#D4AF37` (buttons, highlights)
- Text: `#FFFFFF` (primary), `#B0B0B0` (secondary)
- Success: `#4CAF50` (green)
- Warning: `#FFA726` (orange)
- Danger: `#E53935` (red)

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
      ┌──────┼──────────────┐
      ↓      ↓              ↓
   Minigame  NPC Conv    Discovery
      │      │              │
   ┌──┴──┐ ┌─┴──┐          │
   ↓     ↓ ↓    ↓          │
Success Fail Success Fail  │
   │     │   │    │         │
   └──┬──┘   └─┬──┘         │
      │        │            │
      └────┬───┴────────────┘
           ↓
     Continue Playing
           ↓
      ┌────┴────┐
      ↓         ↓
  Victory   Failure
   Screen    Screen
      │         │
      └────┬────┘
           ↓
    (Play Again or Menu)
```

---

## Screen 1: Landing Page

**Purpose**: First screen - choose to host or join a game

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│         THE CREW 🎭             │
│    Chapter 1: Heist             │
│   Collaborative Heist Game      │
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
- [ ] App title "THE CREW" (large, centered)
- [ ] Chapter subtitle "Chapter 1: Heist" (medium)
- [ ] Tagline "Collaborative Heist Game" (small)
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
│  │   [  A  P  P  L  E  ]   │   │  ← Large input
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
- [ ] 4-5 letter code input (large, auto-caps)
- [ ] "Join" button (disabled until 4-5 letters entered)
- [ ] "Cancel" link
- [ ] Error message area (if invalid code)

**Actions:**
- Enter 4-5 letters → Enable "Join" button
- Tap "Join" → Validate code → Go to Room Lobby
- Tap "Cancel" → Return to Landing Page

---

## Screen 3: Room Lobby (Host View)

**Purpose**: Wait for players, select scenario/roles, start game

### UI Elements:

```
┌─────────────────────────────────┐
│  Room Code: APPLE          📋   │← Copy button
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
│  Room Code: TIGER          📋   │
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
│  👥 WHO'S HERE                  │← Shows others at location
│  ┌───────────────────────────┐ │
│  │ 👤 Sam (Safe Cracker)     │ │← Other player here
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 💬 Security Guard         │ │← NPC here
│  │ Security personnel        │ │
│  └───────────────────────────┘ │
│                                 │
│  YOUR TASKS (Safe Cracker)      │← Shows player's role
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
│  ┌─────┐ ┌─────┐ ┌───────┐     │
│  │ 🗺️  │ │ 🎒  │ │  🔍   │     │← Quick actions
│  │ Map │ │ Bag │ │Search │     │
│  └─────┘ └─────┘ └───────┘     │
│           (3) ↑                 │← Item count badge
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

**Who's Here Section:**
- [ ] Shows other players at current location
  - [ ] Player name and role (e.g., "Sam (Safe Cracker)")
  - [ ] 👤 icon for players
- [ ] Shows NPCs at current location
  - [ ] NPC name and role (e.g., "Security Guard - Security personnel")
  - [ ] 💬 icon for NPCs
- [ ] Only shows if there are players or NPCs present
- [ ] Updates in real-time when players move

**Your Tasks Header:**
- [ ] Shows "YOUR TASKS (role name)" using player's selected role
- [ ] Role name formatted in Title Case (e.g., "Safe Cracker", "Mastermind")

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
- [ ] "🗺️ Map" button → Location view (also shows teammates)
- [ ] "🎒 Bag" button → Inventory screen (shows item count badge)
- [ ] "🔍 Search" button → Search current room (exploration mode)

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
- Tap "🗺️ Map" → Show location map, available locations, and see where teammates are
- Tap "🎒 Bag" → Open inventory screen (Screen 9b)
  - Shows item count badge (number of items)
  - Manage items, transfer, use, or drop
- Tap "🔍 Search" → Open search screen in exploration mode (no specific target)
  - Always available at any location
  - Discover items, trigger new tasks
  - Encourages player communication

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
│  📍 Location: Crew Hideout ✓   │
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

**Purpose**: Show all locations with players, NPCs, and movement options

### UI Elements:

```
┌─────────────────────────────────┐
│  LOCATIONS                  ✕   │
│                                 │
│  CURRENT                        │
│  ┌───────────────────────────┐ │
│  │ 📍 Crew Hideout      ⭐    │ │← You are here
│  │                           │ │
│  │ 👤 You (Hacker)           │ │← Players here
│  │ 👤 Sam (Safe Cracker)     │ │
│  └───────────────────────────┘ │
│                                 │
│  ACCESSIBLE                     │
│  ┌───────────────────────────┐ │
│  │ 🏛️ Grand Hall             │ │← Can travel here
│  │                           │ │
│  │ 💬 Security Guard         │ │← NPC present
│  │ 🎯 2 tasks available      │ │← Tasks here
│  │                           │ │
│  │          [TRAVEL →]       │ │← Travel button
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 🏢 Museum Basement        │ │
│  │                           │ │
│  │ 👤 Alex (Mastermind)      │ │← Teammate here
│  │ 🎯 1 task available       │ │
│  │                           │ │
│  │          [TRAVEL →]       │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 🔒 Vault Room             │ │← Locked
│  │                           │ │
│  │ 🔐 Needs: Vault key       │ │← Requirement
│  │ 🎯 1 task waiting         │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Close button (X in title)
- [ ] Section headers (CURRENT, ACCESSIBLE, LOCKED)
- [ ] Location cards showing:
  - [ ] Location icon and name
  - [ ] Players at this location (👤 icon + name + role)
  - [ ] NPCs at this location (💬 icon + name)
  - [ ] Tasks available count (🎯 icon + count)
  - [ ] Travel button (for accessible locations)
  - [ ] Lock requirement (for locked locations)
- [ ] Current location highlighted (gold border, ⭐ star)
- [ ] Accessible locations (white/tappable)
- [ ] Locked locations (grayed, lock icon 🔒)

**Location Visibility:**
- All players can see ALL locations in the game
- Not limited to locations where they have tasks
- Enables exploration and coordination across the team
- Can travel to any accessible (unlocked) location

**Real-Time Updates:**
- When teammate moves → Their icon moves to new location
- When NPC is talked to → NPC may change mood/status
- When task completed → Task count updates
- When location unlocked → Moves from LOCKED to ACCESSIBLE

**Player Display Rules:**
- Show up to 5 players per location
- If more than 5: "👤 +3 more players"
- Highlight yourself in bold/gold
- Show role in parentheses

**NPC Display Rules:**
- Show NPC name only (no personality)
- Add mood indicator if relevant: 💬 (neutral), 😊 (friendly), 😠 (suspicious)
- Multiple NPCs listed if present

**Task Count:**
- Shows YOUR available tasks at that location
- Completed tasks not counted
- Locked tasks not counted
- Real-time update when tasks unlock/complete

**Actions:**
- Tap accessible location → Move there (update current location, close dialog)
- Tap locked location → Show unlock requirement toast
- Tap player name → Quick view of their status (optional)
- Tap NPC name → Quick view of NPC personality (optional)
- Tap X → Close modal

---

## Screen 9: Team View

**Status**: 🚧 Not yet implemented - Team info is shown in Map View for now

**Purpose**: See what all players are doing

### UI Elements:

```
┌─────────────────────────────────┐
│  TEAM STATUS                ✕   │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 👤 You (Hacker)           │ │
│  │ 📍 Crew Hideout            │ │
│  │ 🎮 Prep Hacking Device    │ │← Current task
│  │ ● In Progress             │ │← Status
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ 👑 Brian (Mastermind)     │ │
│  │ 📍 Crew Hideout            │ │
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

## Screen 9b: Inventory Screen

**Purpose**: Manage your collected items, transfer to others, or use items

### UI Elements:

```
┌─────────────────────────────────┐
│  YOUR INVENTORY            ✕    │
│  📍 Vault Room                  │← Current location
│                                 │
│  YOU HAVE (3):                  │
│                                 │
│  ┌───────────────────────────┐ │
│  │ ┌────┐                    │ │← Item 1
│  │ │📱  │ Burner Phone       │ │  80x80 item image
│  │ │img │ Untraceable phone  │ │  (burner phone photo)
│  │ └────┘                    │ │
│  │ [Transfer] [Use] [Drop]   │ │← Actions
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ ┌────┐                    │ │← Item 2
│  │ │🍎  │ Apple              │ │  80x80 item image
│  │ │img │ Fresh red apple    │ │  (red apple photo)
│  │ └────┘                    │ │
│  │ [Transfer] [Use] [Drop]   │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ ┌────┐                    │ │← Item 3
│  │ │🔑  │ Security Keycard   │ │  80x80 item image
│  │ │img │ Level 2 access     │ │  (keycard photo)
│  │ └────┘                    │ │
│  │ [Transfer] [Use] [Drop]   │ │
│  └───────────────────────────┘ │
│                                 │
│  (Empty slots)                  │
│                                 │
└─────────────────────────────────┘
```

**When "Transfer" is tapped:**

```
┌─────────────────────────────────┐
│  TRANSFER: 🍎 Apple        ✕    │
│                                 │
│  PLAYERS IN THIS ROOM:          │
│  ┌───────────────────────────┐ │
│  │ 👤 Alex (Hacker)          │ │← Teammate here
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 👤 Sam (Safe Cracker)     │ │
│  └───────────────────────────┘ │
│                                 │
│  NPCs IN THIS ROOM:             │
│  ┌───────────────────────────┐ │
│  │ 💬 Brenda Williams        │ │← NPC here
│  │    (train passenger)      │ │
│  └───────────────────────────┘ │
│                                 │
│  ⚠️ No one else in this room    │← If alone
│                                 │
│        Cancel                   │
└─────────────────────────────────┘
```

**When "Use" is tapped:**

```
┌─────────────────────────────────┐
│  USE: 🔑 Security Keycard  ✕    │
│                                 │
│  WHERE TO USE:                  │
│  ┌───────────────────────────┐ │
│  │ 🚪 Security Door          │ │← Usable here
│  │ ✅ Can unlock this!       │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 💻 Computer Terminal      │ │← Not usable
│  │ ⚠️ Wrong item type        │ │
│  └───────────────────────────┘ │
│                                 │
│  Or try using it...             │
│  ┌───────────────────────────┐ │
│  │   TRY TO USE              │ │← Generic try
│  └───────────────────────────┘ │
│                                 │
│        Cancel                   │
└─────────────────────────────────┘
```

**When "Drop" is tapped:**

*Instant action (no confirmation needed):*
- Item removed from inventory immediately
- Small toast notification: "🍎 Apple dropped in Museum Kitchen"
- Item now available in room for others to find
- Can pick it back up by searching room again

**Components:**

**Main Inventory View:**
- [ ] Close button (X)
- [ ] Current location indicator
- [ ] Item count ("YOU HAVE (3):")
- [ ] Item cards (scrollable list)
  - [ ] Item icon (emoji or image)
  - [ ] Item name
  - [ ] Item description/type
  - [ ] Three action buttons per item:
    - [ ] [Transfer] - Give to player/NPC in room
    - [ ] [Use] - Try to use item here
    - [ ] [Drop] - Leave in current room
- [ ] Empty slots indicator
- [ ] Weight/capacity limit (optional future feature)

**Transfer Modal:**
- [ ] Item being transferred (name + icon)
- [ ] "Players in This Room" section
  - [ ] List of teammates at same location
  - [ ] Show role next to name
  - [ ] Tap to transfer to them
- [ ] "NPCs in This Room" section
  - [ ] List of NPCs at same location
  - [ ] Show NPC personality hint
  - [ ] Tap to give item to NPC
- [ ] Empty state message (if alone)
- [ ] Cancel button

**Use Item Modal:**
- [ ] Item being used (name + icon)
- [ ] "Where to Use" section (if obvious targets)
  - [ ] Contextual objects in room
  - [ ] Shows if compatible
- [ ] Generic "Try to Use" button
  - [ ] LLM evaluates if valid
  - [ ] May trigger task completion
  - [ ] May trigger dialogue/event
- [ ] Cancel button

**Drop Action (Instant):**
- [ ] No confirmation modal needed
- [ ] Toast notification (small popup)
- [ ] Shows item dropped and location
- [ ] Auto-dismisses after 2 seconds

**Actions:**

**Main View:**
- Tap item → Expand to show action buttons
- Tap "Transfer" → Open transfer modal
- Tap "Use" → Open use item modal
- Tap "Drop" → Open drop confirmation
- Tap X → Close inventory, return to game screen

**Transfer:**
- Tap player/NPC → Confirm transfer
- Item removed from your inventory
- Item added to recipient's inventory (or consumed by NPC)
- Show success message
- Close modal, return to inventory

**Use:**
- Tap object → Try to use item on it
- Check compatibility
- Success → Item used, may complete task, may trigger event
- Failure → Show message "This item can't be used here"
- Cancel → Return to inventory

**Drop:**
- Tap "Drop" → Item instantly removed from inventory
- Item placed in room's available items
- Toast notification: "🍎 Apple dropped in [Room Name]"
- Other players can find it when searching room
- Can pick it back up by searching room again (no penalty)

**Design Notes:**

**Inventory System Benefits:**
- ✅ Physical item handoffs between players (🤝 tasks)
- ✅ NPC requests (give items to unlock info)
- ✅ Strategic decisions (who should carry what?)
- ✅ Room-based trading (must be in same location)
- ✅ Dropped items persist in rooms
- ✅ Encourages in-person communication ("I have the phone, come get it!")

**Instant Drop (No Confirmation):**
- Drop is instant - no confirmation modal needed
- Rationale: Players can easily pick it back up if mistake
- Reduces friction and taps
- Toast notification provides feedback
- Encourages quick item management

**Smart Use System:**
- Context-aware (shows compatible objects in room)
- LLM-powered fallback ("Try to Use" for creative attempts)
- Friendly failure messages (not just "No")
- May trigger events (using lockpick on door)
- May start conversations (giving food to hungry NPC)

**Transfer Rules:**
- ✅ Can transfer to players in same room
- ✅ Can give to NPCs in same room (they consume it or react)
- ❌ Cannot transfer across rooms (must meet up!)
- Creates coordination challenges ("Meet me at the kitchen")

**Item Types:**
- **Quest items**: Burner phone, keycards, cables, tools
- **Consumables**: Food, drinks (for NPC requests)
- **Key items**: Codes written down, photos, documents
- **Equipment**: Lockpicks, hacking devices, disguises

**Real-Time Updates:**
- Team sees when you transfer items
- Recipient gets notification
- Dropped items appear in room search
- Used items may trigger team-wide events

---

## Screen 10: NPC Conversation Screen

**Purpose**: Chat with an NPC character to extract information

### UI Elements:

```
┌─────────────────────────────────┐
│  < Back                         │
│                                 │
│  🎯 WHAT THE TEAM NEEDS         │
│  ┌───────────────────────────┐ │
│  │ 🟢🟢🟢 Car 7 security    │ │← High confidence
│  │ 🟡🟡⚪ Vault code        │ │← Medium confidence
│  │ 🔴⚪⚪ Escape routes     │ │← Low confidence
│  │                           │ │
│  │ Brenda likely knows       │ │← Summary
│  │ about security!           │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │        [NPC Image]        │ │← Character portrait
│  │     280x280 Borderlands   │ │   (nano-banana)
│  │                           │ │
│  └───────────────────────────┘ │
│                                 │
│       BRENDA WILLIAMS           │
│    chatty, bored, gossipy       │← Personality
│                                 │
│ ┌──── CHAT HISTORY ──────────┐ │
│ │                             │ │
│ │ [Brenda]                    │ │← NPC messages
│ │ Ugh, this train is SO late! │ │   (left-aligned,
│ │ Been waiting forever...     │ │    gray bubble)
│ │                             │ │
│ │              [You]          │ │← Your messages
│ │     Yeah, tell me about it! │ │   (right-aligned,
│ │                             │ │    gold bubble)
│ │                             │ │
│ │ [Brenda]                    │ │
│ │ I overheard the conductor   │ │
│ │ mention something about     │ │
│ │ laser grids in Car 7...     │ │
│ │                             │ │
│ └─────────────────────────────┘ │← Scrollable
│                                 │
│ QUICK RESPONSES:                │
│ ┌─────────────────────────────┐│
│ │ 💬 Tell me more about that  ││← Option 1
│ └─────────────────────────────┘│
│ ┌─────────────────────────────┐│
│ │ 💬 Did you hear anything    ││← Option 2
│ │    else?                    ││
│ └─────────────────────────────┘│
│                                 │
│ ┌─────────────────────────────┐│
│ │ ✍️  Write your own...       ││← Free-form option
│ └─────────────────────────────┘│
│                                 │
└─────────────────────────────────┘
```

**When "Write your own" is tapped:**

```
┌─────────────────────────────────┐
│  < Back                         │
│                                 │
│  🎯 WHAT THE TEAM NEEDS         │
│  🟢🟢🟢 Car 7 security         │← Multiple
│  🟡🟡⚪ Vault code             │   objectives
│  Brenda likely knows security! │   visible
│                                 │
│ ┌──── CHAT HISTORY ──────────┐ │
│ │                             │ │
│ │ [Brenda]                    │ │
│ │ I overheard the conductor   │ │
│ │ mention laser grids...      │ │
│ │                             │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐│
│ │ Type your response...       ││← Text input
│ └─────────────────────────────┘│
│  [SEND] [QUICK RESPONSES]       │← Send + back button
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Back button (returns to game screen)
- [ ] Objective section (always visible at top)
  - [ ] Header adapts to context:
    - "🎯 YOUR OBJECTIVE ✅" (single objective, high confidence)
    - "🎯 WHAT THE TEAM NEEDS" (multiple objectives, mixed confidence)
    - "🎯 WHAT YOU'RE SEEKING ❓" (low confidence overall)
    - "🎯 YOUR OBJECTIVE ⚠️" (action needed - complete request first)
  - [ ] Objective list (1-4 items typically)
    - [ ] Each objective has individual confidence indicator
    - [ ] 🟢🟢🟢 = High (NPC likely knows THIS specific info)
    - [ ] 🟡🟡⚪ = Medium (might know THIS)
    - [ ] 🔴⚪⚪ = Low (probably doesn't know THIS)
    - [ ] 🟠 = Prerequisite (need to complete trade/request first)
  - [ ] Smart summary message below objectives:
    - Highlights what NPC likely knows
    - Examples:
      - "Rosa likely knows about guard schedules!"
      - "Rosa knows all of this!" (if all green)
      - "Tommy probably doesn't know any of this" (if all red)
      - "Eddie might know something" (if mixed)
  - [ ] Shows up to 4 team objectives at once
  - [ ] Compact but readable (4-6 lines total)
  - [ ] Golden/yellow text to stand out
  - [ ] Stays visible while scrolling chat
  - [ ] Provides full context - player can ask about any/all objectives
- [ ] NPC character portrait (large, 280x280px, Borderlands style)
- [ ] NPC name (prominent)
- [ ] NPC personality traits (small text, under name)
- [ ] Chat history area (scrollable)
  - [ ] NPC messages (left-aligned, gray bubble)
  - [ ] Your messages (right-aligned, gold bubble)
  - [ ] Message labels ("Brenda" / "You")
  - [ ] Timestamps (optional)
  - [ ] Auto-scroll to bottom on new messages
- [ ] Quick response options (2-3 pre-written suggestions)
  - [ ] Speech bubble icon 💬
  - [ ] Short, context-appropriate responses
  - [ ] Generated dynamically by LLM based on conversation
- [ ] "Write your own..." button (switches to free-form mode)
  - [ ] Pencil icon ✍️
  - [ ] Opens text input field
- [ ] Text input field (when in free-form mode)
  - [ ] Placeholder: "Type your response..."
  - [ ] Send button
  - [ ] "Quick Responses" button (returns to quick mode)
- [ ] Success/failure indicator (modal overlay)
  - [ ] Green success banner when info obtained
  - [ ] Red failure banner when NPC shuts down

**Hybrid Interaction System:**

**Quick Response Mode (Default):**
- Shows 2-3 contextual response options
- Easy for players who want guidance
- Faster interaction
- Good for new players

**Free-Form Mode:**
- Tap "Write your own..."
- Text input appears
- Full freedom to say anything
- Good for experienced players / social engineering
- Can return to quick responses anytime

**Actions:**
- Tap quick response → Send to LLM → Get NPC reaction → Show new quick options
- Tap "Write your own..." → Show text input field
- Type message → Tap "Send" → Get NPC reaction
- Tap "Quick Responses" → Return to quick response mode
- Success detection (LLM-based) → Show success modal with what was learned
- Failure detection (NPC shuts down) → Show failure modal
- Tap Back → Return to game screen (conversation saved, progress persists)

**Design Notes:**

**When to Show Objectives (Three Scenarios):**

**Scenario 1: NPC Task with Specific Objective**
- Task says: "💬 Talk to Brenda - Learn about Car 7 security"
- Show: "🎯 Find out about Car 7's security systems"
- NPC definitely has this information
- Clear, directed conversation

**Scenario 2: Exploratory NPC Conversation (No Task)**
- Player initiates conversation without specific task
- Show: "🎯 TEAM GOAL: Steal the artifact from the train"
- OR: "💬 See what you can learn from [NPC Name]"
- NPC may or may not have useful info
- Encourages exploration and discovery

**Scenario 3: NPC Request/Trade**
- Task says: "💬 Give Brenda the snack"
- Show: "🎯 Give Brenda chips to build rapport"
- OR: Show both: "🎯 Goal: Learn about security | Give her chips first"
- Clear what you need to do

**General Team Objectives (Always Helpful):**
- Could also show high-level team objective in smaller text
- Example: "🎯 Find security info | Team Goal: Board train safely"
- Provides context even if NPC might not help

**Recommendation:**
- **Specific task** → Show specific objective
- **No task** → Show team objective OR "See what you can learn"
- Always provide context so players aren't wandering blindly

**Visual Examples of Objective Box:**

*SINGLE OBJECTIVE - HIGH CONFIDENCE:*
```
🎯 YOUR OBJECTIVE          ✅
┌───────────────────────────┐
│ Get the loading dock      │
│ access code from Rosa     │
│                           │
│ 🟢🟢🟢 Rosa likely       │← Green = high confidence
│         knows this!       │
└───────────────────────────┘
```

*MULTIPLE OBJECTIVES - Mixed Confidence (Most Common):*
```
🎯 WHAT THE TEAM NEEDS
┌───────────────────────────┐
│ 🟢🟢🟢 Guard schedules   │← High (knows this!)
│ 🟡🟡⚪ Vault code        │← Medium (might know)
│ 🔴⚪⚪ Escape routes     │← Low (probably not)
│                           │
│ Rosa likely knows about   │← Smart summary
│ guard schedules!          │
└───────────────────────────┘
```

*ALL HIGH CONFIDENCE - Jackpot NPC:*
```
🎯 WHAT THE TEAM NEEDS     ✅
┌───────────────────────────┐
│ 🟢🟢🟢 Loading dock code │
│ 🟢🟢🟢 Shift change time │
│ 🟢🟢🟢 Security gaps     │
│                           │
│ Rosa knows all of this!   │← Talk to her!
└───────────────────────────┘
```

*ALL LOW CONFIDENCE - Wrong NPC:*
```
🎯 WHAT YOU'RE SEEKING    ❓
┌───────────────────────────┐
│ 🔴⚪⚪ Vault code        │
│ 🔴⚪⚪ Guard schedule    │
│ 🔴⚪⚪ Escape route      │
│                           │
│ Tommy probably doesn't    │← Try someone else
│ know any of this          │
└───────────────────────────┘
```

*NPC REQUEST (Before Sharing):*
```
🎯 YOUR OBJECTIVE          ⚠️
┌───────────────────────────┐
│ 🟠 Give Brenda chips      │← Must do first
│ 🟢 Then: Learn security   │← After trade
│                           │
│ Complete request first!   │
└───────────────────────────┘
```

*AFTER LEARNING INFO (Progress Update):*
```
🎯 WHAT THE TEAM NEEDS
┌───────────────────────────┐
│ ✅ Guard schedules        │← Learned!
│ 🟡🟡⚪ Vault code        │← Still seeking
│ 🔴⚪⚪ Escape routes     │← Still seeking
│                           │
│ Keep talking, Rosa might  │← Encouragement
│ know more!                │
└───────────────────────────┘
```

*ALL OBJECTIVES COMPLETE:*
```
🎯 OBJECTIVES COMPLETE     🎉
┌───────────────────────────┐
│ ✅ Guard schedules        │
│ ✅ Loading dock code      │
│ ✅ Shift change time      │
│                           │
│ Success! Mission info     │
│ obtained!                 │
└───────────────────────────┘
```

**Confidence Indicator System:**

**🟢🟢🟢 HIGH (Green) - "Likely knows this!"**
- Triggered by: Specific NPC task in your task list
- Task description mentions this NPC by name
- Example: "💬 Talk to Brenda - Learn about Car 7 security"
- Header: "YOUR OBJECTIVE" + ✅
- Message: "[NPC Name] likely knows this!"

**🟡🟡⚪ MEDIUM (Yellow/Gray) - "Might know something"**
- Triggered by: General team objective, no specific NPC task
- Player chose to talk to this NPC on their own
- NPC role/location seems relevant
- Header: "YOUR GOAL" + 🤔
- Message: "[NPC Name] might know something"

**🔴⚪⚪ LOW (Red/Gray) - "Probably doesn't know"**
- Triggered by: Talking to unrelated NPC
- NPC role doesn't match objective type
- Player exploring without direction
- Header: "WHAT YOU'RE SEEKING" + ❓
- Message: "[NPC Name] probably doesn't know"

**🟠🟠🟠 ACTION NEEDED (Orange) - "Complete request first!"**
- Triggered by: NPC requires item/favor before sharing
- You have a prerequisite task
- Example: "Give Brenda chips → She'll share info"
- Header: "YOUR OBJECTIVE" + ⚠️
- Message: "Complete request first!"

**How Confidence is Determined (Per Objective):**

Each objective gets its own confidence rating based on:

**HIGH (🟢🟢🟢) Confidence:**
- Specific task mentions this NPC by name for this objective
- NPC's role directly relates to this info (security guard → guard schedules)
- Generated experience explicitly links NPC to this info
- Task description says "Talk to [NPC] - Learn [specific thing]"

**MEDIUM (🟡🟡⚪) Confidence:**
- NPC's role tangentially relates (parking attendant → security schedules)
- NPC at location relevant to objective (kitchen staff → food locations)
- General connection but not confirmed

**LOW (🔴⚪⚪) Confidence:**
- NPC role unrelated to objective (food vendor → vault codes)
- Random NPC, player exploring
- No logical connection

**ACTION NEEDED (🟠):**
- Prerequisite task exists (give item, complete favor)
- Must do something before NPC will share

**Multiple Objectives Example:**

Team needs 3 things, talking to security guard Rosa:
- 🟢🟢🟢 Guard schedules (her job = definitely knows)
- 🟡🟡⚪ Loading dock access (might know, related)
- 🔴⚪⚪ Vault combination (not her area)

**Conversation Strategy:**
Players can ask about ALL objectives in one conversation:
1. Start with high confidence (🟢) - most likely to succeed
2. If going well, ask about medium (🟡) - worth trying
3. If rapport strong, try low (🔴) - might surprise you!

**Benefits of Per-Objective Confidence:**
- Shows which questions to prioritize
- Players can strategize conversation flow
- One NPC might help with multiple things
- Clear what to ask vs what to skip
- Encourages asking about unexpected connections

**Multi-Objective Conversation Flow:**

**Example conversation with 3 objectives:**

*Start of conversation:*
```
Team Needs:
🟢🟢🟢 Guard schedules
🟡🟡⚪ Vault code
🔴⚪⚪ Escape routes
```

*Player asks about guard schedules → Success!*
```
Team Needs:
✅ Guard schedules        ← Learned!
🟡🟡⚪ Vault code
🔴⚪⚪ Escape routes

Keep talking!
```

*Player asks about vault code → NPC doesn't know*
```
Team Needs:
✅ Guard schedules
❌ Vault code            ← Asked, doesn't know
🔴⚪⚪ Escape routes

Rosa didn't know about vault
```

*Player can still ask about escape routes (worth shot)*

**Benefits:**
- One conversation can cover multiple objectives
- Clear visual progress (checkmarks appear)
- Prioritize high-confidence questions first
- Try medium/low if conversation going well
- Players know what's been covered vs still seeking

**Why Multi-Objective Display:**
- ✅ **Full Context**: Show everything team needs
- ✅ **Priority Guidance**: Green first, then yellow, then red
- ✅ **Efficient Conversations**: Ask multiple things in one chat
- ✅ **Progress Tracking**: Checkmarks show what's learned
- ✅ **Encourage Exploration**: Low confidence still visible (try anyway!)
- ✅ **Realistic**: One NPC can help with multiple things
- ✅ **Strategic**: Players plan question order based on confidence

**Why Confidence Indicators:**
- ✅ **Instant feedback**: Know if you're talking to right person
- ✅ **Reduces frustration**: Don't waste time on wrong NPCs
- ✅ **Encourages exploration**: Medium/low = try anyway, might surprise you
- ✅ **Creates realism**: Not everyone has answers (low confidence NPCs exist)
- ✅ **Strategic decisions**: High confidence = worth social engineering effort
- ✅ **Discovery moments**: Low confidence NPC reveals something = surprise!

**Why Show Objective at Top:**
- ✅ **Constant Reminder**: Players always know what they're trying to learn
- ✅ **Reduces Confusion**: No wondering "what am I doing here?"
- ✅ **Guides Conversation**: Players can steer chat toward goal
- ✅ **Strategic Context**: Helps choose quick responses or craft free-form messages
- ✅ **Success Recognition**: Players know when they've achieved the objective
- ✅ **Works for Wrong NPC**: Even if this NPC can't help, player understands what they're looking for overall

**Why Hybrid Approach:**
- ✅ **Accessibility**: Quick responses lower barrier to entry
- ✅ **Depth**: Free-form allows skilled social engineering
- ✅ **Flexibility**: Players choose their comfort level
- ✅ **Replayability**: Different approaches each time
- ✅ **Difficulty scaling**: Easy mode = use quick responses, Hard mode = need free-form finesse

**Quick Response Generation:**
- Generated by LLM based on:
  - Current conversation context
  - NPC personality
  - Player's objective
  - Difficulty level
- Always include 1 safe option, 1 risky option, 1 creative option
- Update after each exchange

**Visual Inspiration:**
- Based on working prototype: `prototype/npc_chat_test.html`
- Chat UI similar to messaging apps (familiar UX)
- Character portrait from `generate_npc_image.py` (Borderlands style)
- Clean, dark theme matching overall game aesthetic

---

## Screen 10a: NPC Conversation Success Screen

**Purpose**: Show success after obtaining information from NPC

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│       ✅ 🎯 ✨                  │
│                                 │
│   INFORMATION OBTAINED!         │← Large, animated
│                                 │
│       [NPC Portrait]            │
│      BRENDA WILLIAMS            │
│                                 │
│  ╔═══════════════════════════╗ │
│  ║                           ║ │
│  ║  📋 LEARNED:               ║ │
│  ║                           ║ │
│  ║  • Car 7 has laser grid   ║ │← Key info obtained
│  ║  • Disabled at 3:15pm     ║ │
│  ║  • Guard shift change     ║ │
│  ║                           ║ │
│  ║  💎 BONUS INFO:           ║ │
│  ║  Conductor is lazy,       ║ │← Extra details
│  ║  leaves post for coffee   ║ │
│  ║                           ║ │
│  ╚═══════════════════════════╝ │
│                                 │
│  🔓 UPDATED OBJECTIVES:         │
│  ✅ Learn Car 7 security        │← Completed
│  🟢 Plan 3:15pm entry           │← New/unlocked
│                                 │
│  ┌───────────────────────────┐ │
│  │     CONTINUE              │ │← Primary CTA
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Success icon/animation
- [ ] "Information Obtained!" header (green)
- [ ] NPC portrait reminder
- [ ] Information box
  - [ ] Primary information learned (objective-related)
  - [ ] Bonus information (extra context, tips)
- [ ] Updated objectives section
  - [ ] Shows completed objectives (checkmark)
  - [ ] Shows newly unlocked objectives
- [ ] Continue button (returns to game screen)
- [ ] Optional: Share with team button

**Success Triggers:**
- NPC revealed key information
- Objective confidence reached 100%
- Completed trade/request successfully
- Built enough rapport/trust

---

## Screen 10b: NPC Conversation Failure Screen

**Purpose**: Show failure when NPC shuts down or becomes suspicious

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│       ❌ 🚨 ⚠️                  │
│                                 │
│   CONVERSATION ENDED            │← Large, red/orange
│                                 │
│       [NPC Portrait]            │
│      BRENDA WILLIAMS            │
│      😠 Suspicious              │← Mood indicator
│                                 │
│  ╔═══════════════════════════╗ │
│  ║                           ║ │
│  ║  ⚠️  WHAT HAPPENED:        ║ │
│  ║                           ║ │
│  ║  "Wait... why are you     ║ │← NPC's reaction
│  ║   asking so many          ║ │
│  ║   questions about the     ║ │
│  ║   security? That's weird!"║ │
│  ║                           ║ │
│  ║  🚫 CONSEQUENCES:          ║ │
│  ║  • Brenda is now cautious ║ │← Impact
│  ║  • Can't talk to her again║ │
│  ║  • Team reputation -1     ║ │
│  ║                           ║ │
│  ╚═══════════════════════════╝ │
│                                 │
│  💡 TIP: Build rapport first    │
│     before asking direct        │← Helpful hint
│     questions about security.   │
│                                 │
│  🔄 ALTERNATIVE OPTIONS:        │
│  • Ask another NPC (Tommy)      │← Next steps
│  • Search for security logs     │
│                                 │
│  ┌───────────────────────────┐ │
│  │     CONTINUE              │ │← Primary CTA
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Failure/warning icon
- [ ] "Conversation Ended" header (red/orange)
- [ ] NPC portrait with updated mood (angry, suspicious, closed)
- [ ] What Happened box
  - [ ] NPC's reaction quote
  - [ ] Why they shut down
- [ ] Consequences box
  - [ ] Impact on game state
  - [ ] Reputation/alarm changes
  - [ ] Future limitations
- [ ] Tip (how to avoid next time)
- [ ] Alternative options (other NPCs, other approaches)
- [ ] Continue button (returns to game screen)

**Failure Triggers:**
- Asked too direct/suspicious questions
- Failed trade/request
- Reputation too low
- NPC personality clash
- Time pressure/rushed
- Asked about info they don't know (frustration)

**Animations:**
- NPC portrait changes expression (0.3s)
- Red warning flash (0.5s)
- Consequences fade in (0.2s each)

---

## Screen 11: Search/Hunt Screen

**Purpose**: Search a location for items or explore to discover new things

### Currently Implemented: Search Results List

The current implementation shows a simpler list-based search results:

```
┌─────────────────────────────────┐
│  🔍 Search Results: Crew Hideout ✕│
│                                 │
│  ┌───────────────────────────┐ │
│  │ ┌────┐                    │ │
│  │ │🔧  │ Safe Cracking Tools│ │← 80x80 item image
│  │ │img │ Professional lock  │ │
│  │ └────┘ pick set...        │ │
│  │ Required for: SC2         │ │
│  │        [Pick Up]          │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ ┌────┐                    │ │
│  │ │📻  │ Radio Earpiece Set │ │← 80x80 item image
│  │ │img │ Two-way radio      │ │
│  │ └────┘ earpieces          │ │
│  │ Required for: MM2         │ │
│  │        [Pick Up]          │ │
│  └───────────────────────────┘ │
│                                 │
│  (No items found if empty)      │
└─────────────────────────────────┘
```

**Components:**
- [ ] Location name in header
- [ ] Close button (X)
- [ ] Item cards (scrollable list)
  - [ ] 80x80 item image thumbnail
  - [ ] Item name
  - [ ] Item description (truncated)
  - [ ] "Required for" hint (if applicable)
  - [ ] Pick Up button
- [ ] Empty state message

### Mode 1: Specific Search Task (Knows Target) [Future]

When player has a task like "🔍 Search: Hunt for Burner Phone"

```
┌─────────────────────────────────┐
│  < Back                         │
│                                 │
│  🔍 SEARCHING                   │
│  Crew Hideout - Office          │
│                                 │
│  📋 TASK: Find Burner Phone     │← From task
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

### Mode 2: General Exploration (No Specific Target)

When player just wants to look around without a task

```
┌─────────────────────────────────┐
│  < Back                         │
│                                 │
│  🔍 EXPLORING                   │
│  Museum Kitchen                 │
│                                 │
│  💡 See what you can find...    │← No specific target
│                                 │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │   🍞  🥤  🍎  🗄️        │ │← Different items
│  │                           │ │
│  │   🔪  🍔  ☕  🧊        │ │
│  │                           │ │
│  └───────────────────────────┘ │
│                                 │
│  Tap items to examine...        │
│  Items found: 🍎 🥤            │← Inventory shown
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Back button
- [ ] Location name
- [ ] Mode indicator (SEARCHING vs EXPLORING)
- [ ] Task description (if specific search)
  - [ ] Only shown when have search task
  - [ ] Shows what you're looking for
- [ ] General exploration hint (if no specific target)
  - [ ] "See what you can find..."
  - [ ] Encourages discovery
- [ ] Interactive area with items to tap
  - [ ] Room-specific items (context-aware)
  - [ ] Visual feedback on tap
- [ ] Items found counter (exploration mode)
  - [ ] Shows collected items
  - [ ] Goes into player inventory
- [ ] Instruction text

**Two Search Modes:**

**Specific Task Search:**
- Have a task that says "🔍 Hunt for X"
- Screen shows "Looking for: X"
- Tapping correct item completes task immediately
- Tapping wrong items gives hints
- Clear success state

**General Exploration:**
- No active search task
- Can search any room from map
- Discover items that might be useful later
- Items go into inventory
- Team members can share what they found (verbal communication!)
- May trigger discovery tasks

**Actions:**

**Specific Search Mode:**
- Tap wrong items → "Not here" or hint feedback
- Tap correct item → Success animation → Item found → Task complete → Return to game screen

**Exploration Mode:**
- Tap items → Examine them
- Find useful items → Add to inventory with animation
- Find quest items → May trigger new tasks
- Nothing found → Try other items
- Can search multiple times
- Tap Back → Return to game with items collected

**Design Notes:**

**Why General Exploration:**
- ✅ Encourages player communication ("Has anyone found cable?")
- ✅ Creates emergent gameplay (find things before you know you need them)
- ✅ Rewards thorough players
- ✅ Builds tension (searching without knowing what's important)
- ✅ More D&D-like (exploring and discovering)

**Room Inventory System:**
- Each room has searchable items
- Some items are quest-critical (burner phone, cable)
- Some items are useful but not required (snacks, coffee, tools)
- Some items are flavor/red herrings (magazines, photos)
- Items persist (if someone already found it, it's gone)
- Real-time updates (if teammate finds something, you see it's gone)

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

## Screen 12a: Minigame Success Screen

**Purpose**: Show success feedback after completing a minigame

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│         ✅ 🎉                   │
│                                 │
│     TASK COMPLETE!              │← Large, animated
│                                 │
│   Connected all wires           │← What they did
│   correctly in 42 seconds       │
│                                 │
│  ╔═══════════════════════════╗ │
│  ║                           ║ │
│  ║  ⭐⭐⭐ PERFECT!         ║ │← Performance rating
│  ║                           ║ │
│  ║  ⚡ Speed Bonus: +50 pts  ║ │← Bonuses (optional)
│  ║  🎯 No Mistakes: +25 pts  ║ │
│  ║                           ║ │
│  ╚═══════════════════════════╝ │
│                                 │
│  🔓 NEXT TASKS UNLOCKED:        │
│  • Check vault interior         │← Tasks unlocked
│  • Radio team to proceed        │   by success
│                                 │
│  ┌───────────────────────────┐ │
│  │     CONTINUE              │ │← Primary CTA
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Success icon/animation (checkmark, confetti)
- [ ] "Task Complete!" header (large, green)
- [ ] Description of what was accomplished
- [ ] Performance rating (stars or grade)
- [ ] Optional bonuses/stats (speed, accuracy, no mistakes)
- [ ] Unlocked tasks preview (what's next)
- [ ] Continue button (returns to game screen)

**Animations:**
1. Confetti/sparkle animation from top (0.5s)
2. Success message fades in with scale effect (0.3s)
3. Stats reveal sequentially (0.2s each)
4. Unlocked tasks slide in from bottom (0.5s)

---

## Screen 12b: Minigame Failure Screen

**Purpose**: Show failure feedback and retry option

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│         ❌ 💥                   │
│                                 │
│     TASK FAILED                 │← Large, red
│                                 │
│   Wire connection incorrect.    │← What went wrong
│   Security system detected      │
│   the attempt.                  │
│                                 │
│  ╔═══════════════════════════╗ │
│  ║                           ║ │
│  ║  ⚠️  CONSEQUENCES          ║ │
│  ║                           ║ │
│  ║  • Alarm triggered        ║ │← Game impact
│  ║  • Time penalty: -2 min   ║ │
│  ║  • Guards alerted         ║ │
│  ║                           ║ │
│  ╚═══════════════════════════╝ │
│                                 │
│  💡 TIP: Watch the wire colors  │
│     carefully. Red connects to  │← Helpful hint
│     the top-right port.         │
│                                 │
│  ┌───────────────────────────┐ │
│  │     TRY AGAIN             │ │← Primary CTA
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │     SKIP (RISKY)          │ │← Secondary option
│  └───────────────────────────┘ │
│                                 │
│        Back to Tasks            │← Tertiary
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Failure icon (X, broken icon, alert)
- [ ] "Task Failed" header (large, red)
- [ ] Description of what went wrong
- [ ] Consequences box
  - [ ] Impact on game state (alarms, time, difficulty)
  - [ ] What changed for the team
- [ ] Helpful tip (specific to the failure)
- [ ] Try Again button (restart minigame)
- [ ] Skip button (continue without completing, may have penalties)
- [ ] Back to Tasks link (abandon this task)

**Animations:**
- Shake animation on failure (0.3s)
- Red flash/pulse effect (0.5s)
- Consequences fade in sequentially (0.2s each)

**Failure Reasons (Examples):**
- Time ran out
- Too many mistakes
- Wrong sequence
- Detection/caught
- Broke tool/item

---

## Screen 13: Victory Screen

**Purpose**: Celebrate successful heist with performance metrics and celebration graphics

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│    ✨ 💎 🎉 💎 ✨              │← Celebration graphics
│                                 │
│    HEIST SUCCESSFUL!            │← Large, bold, animated
│                                 │
│       ⭐ ⭐ ⭐ ⭐ ⭐           │← 5 stars (gold/filled)
│                                 │← Based on performance
│    "Outstanding Work!"          │← Rating message
│                                 │
│  ╔═══════════════════════════╗ │
│  ║                           ║ │
│  ║  ⏱️  TIME TAKEN            ║ │
│  ║     18 min 42 sec         ║ │← Large time display
│  ║                           ║ │
│  ║  🎯 STEALTH BONUS         ║ │
│  ║     No alarms triggered   ║ │
│  ║                           ║ │
│  ║  💰 LOOT SECURED          ║ │
│  ║     $2.4 Million          ║ │
│  ║                           ║ │
│  ╚═══════════════════════════╝ │
│                                 │
│  👥 TEAM PERFORMANCE            │
│                                 │
│  🥇 Sam (Safe Cracker)          │
│     15 tasks completed          │
│                                 │
│  🥈 Alex (Mastermind)           │
│     13 tasks completed          │
│                                 │
│  🥉 Jordan (Lookout)            │
│     11 tasks completed          │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🔄 PLAY AGAIN           │ │← Primary CTA (gold)
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🎲 TRY NEW SCENARIO     │ │← Secondary
│  └───────────────────────────┘ │
│                                 │
│        Back to Menu             │
│                                 │
└─────────────────────────────────┘
```

**Star Rating System (1-5 stars):**
- ⭐⭐⭐⭐⭐ (5 stars): "Perfect Execution!" - Completed in <15 min, no alarms
- ⭐⭐⭐⭐☆ (4 stars): "Outstanding Work!" - Completed in <20 min, 0-1 alarms
- ⭐⭐⭐☆☆ (3 stars): "Job Well Done!" - Completed in <25 min, 0-2 alarms
- ⭐⭐☆☆☆ (2 stars): "Barely Made It" - Completed in <30 min, 3+ alarms
- ⭐☆☆☆☆ (1 star): "Mission Complete" - Completed (any time/conditions)

**Performance Metrics:**
- **Time Taken**: MM:SS format (large, prominent)
- **Stealth Bonus**: Shows if no alarms triggered
- **Loot Value**: Total score/value secured (scenario-specific)
- **Tasks Completed**: X/Y tasks
- **Team Rankings**: Medal icons (🥇🥈🥉) for top 3 players

**Animation States:**
1. **Initial** (0.0s): Screen fades in from black
2. **Celebration** (0.5s): Confetti/sparkles animation from top
3. **Stars Appear** (1.0s): Stars fill in one-by-one with "ding" sound
4. **Stats Reveal** (1.5s): Stats box slides up from bottom
5. **Team Rankings** (2.5s): Player cards fade in sequentially

**Components:**
- [ ] Animated celebration graphics (confetti, sparkles, gems)
- [ ] Large "HEIST SUCCESSFUL!" header with glow effect
- [ ] Dynamic 1-5 star rating with fill animation
- [ ] Performance rating message (changes based on stars)
- [ ] Stats card with gradient border (gold for 5★, silver for 4★, bronze for 3★)
  - [ ] Time taken (large, prominent)
  - [ ] Stealth bonus indicator
  - [ ] Loot/score value
- [ ] Team performance section
  - [ ] Medal icons (🥇🥈🥉) for rankings
  - [ ] Player name + role
  - [ ] Individual task count
- [ ] "Play Again" button (primary CTA, gold)
- [ ] "Try New Scenario" button (secondary)
- [ ] "Back to Menu" link
- [ ] Optional: Confetti particle effect (CSS/canvas)
- [ ] Optional: Victory jingle sound effect

**Visual Styling:**
- Background: Radial gradient from dark center to lighter edges (spotlight effect)
- Stars: Large (32px), gold fill (#D4AF37) with subtle pulsing animation
- Stats card: Dark background (#1E1E1E) with colored border based on rating
- Typography: Extra-large success message (36px bold), prominent time (28px)
- Celebration icons: Animated with slight bounce/rotation
- Team cards: Subtle hover/press effect

**Actions:**
- Tap "Play Again" → Generate new experience, same scenario/roles, go to game screen
- Tap "Try New Scenario" → Return to room lobby (keep same team)
- Tap "Back to Menu" → Disconnect, return to landing page
- Optional: Tap star rating → Show detailed breakdown modal

---

## Screen 14: Failure Screen

**Purpose**: Show results when heist fails

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│      🚨 💥 🚨                   │← Failure graphics
│                                 │
│    HEIST FAILED                 │← Large, bold red text
│                                 │
│   "Caught by Security"          │← Failure reason
│                                 │
│  ╔═══════════════════════════╗ │
│  ║                           ║ │
│  ║  ⏱️  LASTED                ║ │
│  ║     12 min 18 sec         ║ │
│  ║                           ║ │
│  ║  ⚠️  WHAT WENT WRONG      ║ │
│  ║     • Tripped alarm       ║ │
│  ║     • Guards alerted      ║ │
│  ║     • Failed escape       ║ │
│  ║                           ║ │
│  ║  ✅ TASKS COMPLETED       ║ │
│  ║     18 / 45 (40%)         ║ │
│  ║                           ║ │
│  ╚═══════════════════════════╝ │
│                                 │
│  💡 TIP FOR NEXT TIME           │
│                                 │
│  "Coordinate with your team     │
│   before triggering alarms.     │
│   Use the Team View to check    │
│   everyone's status."           │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🔄 TRY AGAIN            │ │← Primary CTA
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │   📋 REVIEW TASKS         │ │← Show what was left
│  └───────────────────────────┘ │
│                                 │
│        Back to Menu             │
│                                 │
└─────────────────────────────────┘
```

**Failure Reasons:**
- **Caught by Security**: Alarm triggered, guards arrived
- **Time Ran Out**: Exceeded time limit
- **Team Conflict**: Player disconnected at critical moment
- **Discovery Failed**: Couldn't find required information
- **Escape Route Blocked**: Failed to secure exit

**Components:**
- [ ] Failure graphic (red theme, alarm icons)
- [ ] "HEIST FAILED" header (red, bold)
- [ ] Failure reason (specific to what went wrong)
- [ ] Stats card (red border)
  - [ ] Time lasted
  - [ ] What went wrong (bullet points)
  - [ ] Tasks completed percentage
- [ ] Tip for next time (helpful hint based on failure reason)
- [ ] "Try Again" button (primary, restart with same setup)
- [ ] "Review Tasks" button (see what was left undone)
- [ ] "Back to Menu" link

**Visual Styling:**
- Background: Dark with red tint/vignette
- Header: Red text (#E53935) with subtle shake animation
- Stats card: Dark background with red border
- Icons: Warning/alert themed (🚨⚠️💥🔴)
- Tip box: Info blue background (#2196F3) to stand out positively

**Actions:**
- Tap "Try Again" → Restart experience with same team/scenario
- Tap "Review Tasks" → Show task list modal (what was completed vs. remaining)
- Tap "Back to Menu" → Disconnect, return to landing page

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
11. ✅ Map View
12. ✅ Team View
13. ✅ Inventory Screen (transfer, use, drop items)
14. ✅ NPC Conversation (hybrid: quick responses + free-form text)
15. ✅ Search Screen (two modes: specific task search + general exploration)

**Phase 3 (Nice to Have):**
16. ✅ Minigame Screens (build 2-3 examples)
17. ✅ Minigame Success/Failure States (feedback and retry)
18. ✅ NPC Conversation Success/Failure States (info obtained / shut down)
19. ✅ Victory Screen (with star rating, time, celebration graphics)
20. ✅ Failure Screen (with tips and retry options)

---

## Screen 16: Game End Screen (Victory)

**Purpose**: Celebrate successful heist completion with the crew

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│  [Crew Celebration Image]       │
│  (Generated image of 3-4 crew   │
│   members in celebratory pose)  │
│                                 │
├─────────────────────────────────┤
│                                 │
│    🎉 HEIST COMPLETE! 🎉        │
│                                 │
│  "Another job well done for     │
│   the crew. The Eye of Orion    │
│   is yours, and the city will   │
│   never know what hit them."    │
│                                 │
├─────────────────────────────────┤
│                                 │
│  THE STORY                      │
│  ─────────────────────          │
│  The crew set out to steal the  │
│  legendary Eye of Orion jewels  │
│  from the museum's high-security│
│  vault during the annual gala.  │
│                                 │
│  Through careful planning,      │
│  social engineering, and expert │
│  safe-cracking, the team pulled │
│  off the impossible and escaped │
│  with $12 million in priceless  │
│  gemstones.                     │
│                                 │
│  THE CREW                       │
│  ─────────────────────          │
│  • [Player 1] as Mastermind     │
│  • [Player 2] as Safe Cracker   │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🏠 Return to Menu       │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🔄 Play Again           │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Crew celebration image (generated AI art, shows 3-4 role characters together)
- [ ] Success headline with celebration emojis
- [ ] Flavor text (heist-themed congratulations message)
- [ ] Story summary section (brief recap of the heist objective and outcome)
- [ ] The Crew section (list of players and their roles)
- [ ] "Return to Menu" button (primary CTA)
- [ ] "Play Again" button (secondary, if host)

**Visual Design:**
- Background: Dark with subtle celebration confetti/sparkles overlay
- Accent: Gold/success green highlights
- Image: Full-width at top (aspect ratio ~16:9), celebrates the crew's roles
- Typography: Bold headline, readable story text
- Spacing: Generous padding around all elements
- Animation: Subtle confetti or shimmer effect in background

**Interaction:**
1. Game ends with success
2. Show crew celebration image generation loading state (1-2 seconds)
3. Animate in celebration message
4. Display story summary and crew list
5. Buttons fade in last
6. "Return to Menu" disconnects WebSocket and returns to landing page
7. "Play Again" (host only) creates new room with same scenario

**Success Message Variations** (randomly selected):
- "Another job well done for the crew. [Target] is yours, and the city will never know what hit them."
- "Clean getaway, no traces left behind. The crew strikes again."
- "Perfect execution. [Target] secured, and not a single alarm tripped."
- "They'll be talking about this heist for years. Well done, crew."
- "In and out, just like the plan. The crew doesn't miss."

---

## Screen 17: Game End Screen (Failure)

**Purpose**: Show failed heist outcome with option to retry

### UI Elements:

```
┌─────────────────────────────────┐
│                                 │
│  [Crew Caught Image]            │
│  (Generated image of crew       │
│   members in custody/retreat)   │
│                                 │
├─────────────────────────────────┤
│                                 │
│    ❌ HEIST FAILED ❌           │
│                                 │
│  "The crew got sloppy. The      │
│   guards were tipped off and    │
│   the heist fell apart."        │
│                                 │
├─────────────────────────────────┤
│                                 │
│  WHAT WENT WRONG                │
│  ─────────────────────          │
│  [Backend-generated summary     │
│   of what caused the failure:   │
│   time ran out, suspicion too   │
│   high, critical task missed]   │
│                                 │
│  THE CREW                       │
│  ─────────────────────          │
│  • [Player 1] as Mastermind     │
│  • [Player 2] as Safe Cracker   │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🏠 Return to Menu       │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🔄 Try Again            │ │
│  └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Crew failure image (police lights, retreat scene, etc.)
- [ ] Failure headline with warning icon
- [ ] Flavor text (heist-themed failure message)
- [ ] "What Went Wrong" section (backend-provided failure reason)
- [ ] The Crew section (list of players and their roles)
- [ ] "Return to Menu" button (primary CTA)
- [ ] "Try Again" button (secondary, if host)

**Visual Design:**
- Background: Dark with red/warning color accents
- Accent: Red/danger color for failure state
- Image: Full-width at top, dramatic failure scene
- Typography: Clear failure message, instructive text
- No celebration effects, more somber tone

**Failure Message Variations** (randomly selected):
- "The crew got sloppy. The guards were tipped off and the heist fell apart."
- "Sirens in the distance. Time to scatter. Better luck next time, crew."
- "The plan fell apart. Sometimes even the best crews make mistakes."
- "Busted. The crew will have to lay low for a while."
- "Not every heist goes as planned. Regroup and try again."

---

## 🚀 Next Steps

1. Review these mockups
2. Create high-fidelity designs (Figma optional)
3. Start Flutter project
4. Build screens in priority order
5. Connect to WebSocket backend

---

## 📸 Image Asset Specifications

### Location Images

**Usage**: Shown at the top of the game screen when at a location

**Specifications**:
- **Dimensions**: 300x150px (2:1 aspect ratio)
- **Style**: Borderlands cel-shaded art style (thick black outlines, stylized)
- **Tone**: Dark, noir atmosphere
- **Content**: Interior or exterior view of the location
- **File Format**: PNG or WebP
- **Naming**: `location_[location_id].png` (e.g., `location_crew_hideout.png`)

**Examples**:
- Crew Hideout: Dark room with planning table, maps on wall
- Museum Grand Hall: Elegant hall with chandeliers, guests
- Vault Room: Heavy steel vault door, dim lighting
- Museum Basement: Concrete corridor, pipes, service entrance

### Item Images

**Usage**: Shown in inventory and search results

**Specifications**:
- **Dimensions**: 80x80px (1:1 square)
- **Style**: Photo-realistic or stylized product shot
- **Background**: Transparent or subtle gradient
- **Lighting**: Well-lit, clear details visible
- **File Format**: PNG with transparency
- **Naming**: `item_[item_id].png` (e.g., `item_burner_phone.png`)

**Examples**:
- Burner Phone: Black flip phone on dark background
- Safe Cracking Tools: Lockpick set in leather case
- Security Keycard: White/blue access card with stripe
- Radio Earpiece: Small black earpiece with wire
- Apple: Red apple (if food items are in the game)

### NPC Portrait Images

**Usage**: Shown in NPC conversation screen (already implemented)

**Specifications**:
- **Dimensions**: 280x280px (1:1 square)
- **Style**: Borderlands cel-shaded art style
- **Content**: Character portrait, shoulders up
- **Expression**: Matches NPC personality (bored, stressed, etc.)
- **File Format**: PNG
- **Naming**: `npc_[npc_id].png` (e.g., `npc_security_guard_marcus.png`)

### Image Generation Priority

1. **High Priority**: Item images (needed for inventory/search functionality)
2. **High Priority**: Location images (needed for immersion on game screen)
3. **Medium Priority**: Additional NPC portraits (some already exist)

### Technical Notes

- All images should be optimized for web (compressed but high quality)
- Consider generating 2x versions for retina displays
- Store in `frontend/web/assets/images/` directory or serve from backend
- Reference in Flutter using `AssetImage` or network URLs
- Lazy load images to improve performance
- Use placeholder images while loading

---
---

# LOBBY OVERHAUL — New Screens (replaces Screen 3)

> Replaces the old "Room Lobby" (Screen 3 above) with two new screens:
> a simplified **Lobby** and a **Scenario Details + Role Claim** screen.

## Updated Screen Flow

```
Landing Page
    ↓
    ├─→ Create Room → New Lobby (Host)
    └─→ Join Room  → New Lobby (Player)
                ↓
        (Host hits Continue — room locks)
                ↓
        Scenario Details + Role Claim
           ├─→ Quick Start: roles pre-assigned, claim one
           └─→ Custom: pick any role, wait for generation
                ↓
        (Host hits Start Game)
                ↓
           Game Screen
                ↓
           (same as before)
```

---

## New Screen 3: Lobby (Host View)

**Purpose**: Assemble the crew and choose a scenario. No role selection here.

```
┌─────────────────────────────────┐
│  ←                   Room Lobby │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Room Code: DECK      📋  │  │  ← Large, copyable
│  │  (2 of 12 players)         │  │
│  └───────────────────────────┘  │
│                                 │
│  🎬 SCENARIO                    │
│  ┌───────────────────────────┐  │
│  │ ┌─────┐                    │  │
│  │ │ 🏛️  │ Museum Gala Vault  │  │  ← Tap opens selector
│  │ │     │ Steal the jewels   │  │    (host only)
│  │ └─────┘ from the vault...  >  │
│  └───────────────────────────┘  │
│  Tap to browse all scenarios     │
│                                 │
│  👥 PLAYERS                     │
│  ┌───────────────────────────┐  │
│  │ 👑 Brandon        ● online│  │  ← Host (crown)
│  │ 👤 Alex           ● online│  │
│  └───────────────────────────┘  │
│                                 │
│  When your crew is here,        │
│  hit Continue                   │
│                                 │
│  ┌───────────────────────────┐  │
│  │      CONTINUE  →           │  │  ← Enabled (2+ players
│  └───────────────────────────┘  │    + scenario selected)
│                                 │
│        Leave Room               │
└─────────────────────────────────┘
```

**Components:**
- [ ] Room code (large, prominent, copyable)
- [ ] Player count indicator
- [ ] Scenario card (host: tappable opens ScenarioSelectionModal; non-host: read-only)
- [ ] Player list (name + online indicator, no roles)
- [ ] Hint text: "When your crew is here, hit Continue"
- [ ] "Continue" button (host only; enabled when 2+ players AND scenario selected)
- [ ] "Leave Room" link

**Actions:**
- Host taps scenario card → opens existing ScenarioSelectionModal
- Host taps "Continue" → sends `lobby_advance` WS → room locks → all navigate to Scenario Details
- Non-host sees "Waiting for host to continue..." instead of button

---

## New Screen 3: Lobby (Non-Host View)

```
┌─────────────────────────────────┐
│  ←                   Room Lobby │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Room Code: DECK      📋  │  │
│  │  (2 of 12 players)         │  │
│  └───────────────────────────┘  │
│                                 │
│  🎬 SCENARIO                    │
│  ┌───────────────────────────┐  │
│  │ ┌─────┐                    │  │
│  │ │ 🏛️  │ Museum Gala Vault  │  │  ← Read-only
│  │ │     │ Steal the jewels   │  │    (can see, can't change)
│  │ └─────┘ from the vault...  │  │
│  └───────────────────────────┘  │
│                                 │
│  👥 PLAYERS                     │
│  ┌───────────────────────────┐  │
│  │ 👑 Brandon        ● online│  │
│  │ 👤 You            ● online│  │
│  └───────────────────────────┘  │
│                                 │
│                                 │
│   ⏳ Waiting for host            │
│      to continue...              │
│                                 │
│                                 │
│        Leave Room               │
└─────────────────────────────────┘
```

---

## New Screen 4: Scenario Details + Role Claim

**Purpose**: Choose Quick Start (pre-generated, instant play) or Custom (any role, generation wait). Claim roles and pick difficulty here.

### Host View — Before Roles Claimed

```
┌─────────────────────────────────┐
│  ←  Scenario Details            │
│                                 │
│  ┌───────────────────────────┐  │
│  │                            │  │
│  │    [scenario art image]    │  │  ← Museum Gala Vault art
│  │                            │  │
│  │  Museum Gala Vault Heist   │  │
│  │  Steal the jewels from     │  │
│  │  the vault during a        │  │
│  │  black-tie event.          │  │
│  └───────────────────────────┘  │
│                                 │
│  ⚡ QUICK START                  │
│  Ready to play — no wait!       │
│  ┌───────────────────────────┐  │
│  │                            │  │
│  │  Museum Gala Vault         │  │
│  │  2 Players                 │  │
│  │                            │  │
│  │  ┌──────┐  ┌──────┐       │  │
│  │  │ 🔐   │  │ 🐱   │       │  │  ← Role avatars
│  │  │Safe  │  │Cat   │       │  │
│  │  │Crack.│  │Burg. │       │  │
│  │  │      │  │      │       │  │
│  │  │ CLAIM│  │ CLAIM│       │  │  ← Tap to claim
│  │  └──────┘  └──────┘       │  │
│  │                            │  │
│  └───────────────────────────┘  │
│                                 │
│  🎨 CUSTOM GAME                 │
│  ┌───────────────────────────┐  │
│  │  Choose any role with any  │  │
│  │  scenario backdrop.        │  │
│  │                            │  │
│  │  ⚠️ ~2 min to generate     │  │
│  │                            │  │
│  │  [ Choose Your Role  > ]   │  │  ← Opens role picker
│  └───────────────────────────┘  │
│                                 │
│  ┌───────────────────────────┐  │
│  │    START GAME  🚀          │  │  ← Disabled until all
│  └───────────────────────────┘  │    players have roles
│                                 │
└─────────────────────────────────┘
```

### After Claiming a Quick Start Role

```
┌─────────────────────────────────┐
│  ←  Scenario Details            │
│                                 │
│  ┌───────────────────────────┐  │
│  │    [scenario art image]    │  │
│  │  Museum Gala Vault Heist   │  │
│  └───────────────────────────┘  │
│                                 │
│  ⚡ QUICK START                  │
│  ┌───────────────────────────┐  │
│  │                            │  │
│  │  ┌──────┐  ┌──────┐       │  │
│  │  │ 🔐   │  │ 🐱   │       │  │
│  │  │Safe  │  │Cat   │       │  │
│  │  │Crack.│  │Burg. │       │  │
│  │  │      │  │      │       │  │
│  │  │👑 You│  │ CLAIM│       │  │  ← You claimed this
│  │  └──────┘  └──────┘       │  │
│  │                            │  │
│  │  Difficulty:               │  │
│  │  [Easy] [MEDIUM] [Hard]    │  │  ← Appears after claim
│  │                            │  │
│  └───────────────────────────┘  │
│                                 │
│  🎨 CUSTOM GAME                 │
│  ┌───────────────────────────┐  │
│  │  [ Choose Your Role  > ]   │  │
│  │  ⚠️ ~2 min to generate     │  │
│  └───────────────────────────┘  │
│                                 │
│  Waiting for 1 more player      │
│  to claim a role...             │
│                                 │
│  ┌───────────────────────────┐  │
│  │    START GAME  🚀          │  │  ← Still disabled
│  └───────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

### All Roles Claimed — Ready to Start

```
┌─────────────────────────────────┐
│  ←  Scenario Details            │
│                                 │
│  ┌───────────────────────────┐  │
│  │    [scenario art image]    │  │
│  │  Museum Gala Vault Heist   │  │
│  └───────────────────────────┘  │
│                                 │
│  ⚡ QUICK START                  │
│  ┌───────────────────────────┐  │
│  │                            │  │
│  │  ┌──────┐  ┌──────┐       │  │
│  │  │ 🔐   │  │ 🐱   │       │  │
│  │  │Safe  │  │Cat   │       │  │
│  │  │Crack.│  │Burg. │       │  │
│  │  │      │  │      │       │  │
│  │  │👑 You│  │👤Alex│       │  │  ← Both claimed
│  │  └──────┘  └──────┘       │  │
│  │                            │  │
│  │  Your difficulty:          │  │
│  │  [Easy] [MEDIUM] [Hard]    │  │
│  │                            │  │
│  └───────────────────────────┘  │
│                                 │
│  ✅ All players ready!           │
│                                 │
│  ┌───────────────────────────┐  │
│  │    START GAME  🚀          │  │  ← ENABLED (host)
│  └───────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

**Components:**
- [ ] Back arrow (host only — sends `lobby_retreat`, re-opens room, returns to Lobby)
- [ ] Scenario header with art image and description
- [ ] Quick Start section (only shown if pre-generated package exists for this player count)
  - [ ] Role cards with avatars
  - [ ] "CLAIM" button on unclaimed roles
  - [ ] Player name on claimed roles
  - [ ] Difficulty toggle (Easy / Medium / Hard) — appears after you claim a role
- [ ] Custom Game section
  - [ ] "Choose Your Role" button → opens existing RoleSelectionModal
  - [ ] Generation time warning
- [ ] Status text ("Waiting for N more players..." / "All players ready!")
- [ ] "Start Game" button (host only; enabled when all players have roles)

**Actions:**
- Tap "CLAIM" on a Quick Start role → sends `select_role` WS message
- Tap difficulty → sends updated `select_role` with new difficulty
- Tap "Choose Your Role" in Custom → opens RoleSelectionModal → sends `select_role`
- Host taps "Start Game":
  - Quick Start path → loads pre-generated scenario (instant)
  - Custom path → triggers generation pipeline (shows progress modal)
- Host taps Back arrow → sends `lobby_retreat` → room re-opens → everyone returns to Lobby

**State Rules:**
- A player can only have one role (Quick Start OR Custom, not both)
- If a player switches from Quick Start to Custom (or vice versa), their previous role is released
- Quick Start "CLAIM" buttons are first-come-first-served; if taken, shows "Taken by [name]"
- Non-host sees "Waiting for host to start..." instead of Start Game button
- If a player disconnects, their claimed role is released

