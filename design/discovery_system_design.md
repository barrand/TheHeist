# Discovery System Design

## 🎯 Core Concept

The game uses a **layered task system** where players start with high-level objectives and discover specific tasks through gameplay. This creates mystery, surprise, and "aha!" moments while maintaining clear goals.

---

## 📊 Task Hierarchy

### 1. **Team Objectives** (Top Level)
High-level goals visible to all players from the start.

**Examples:**
- "Get Into the Safe"
- "Escape the Building"
- "Steal the Diamond"

**Characteristics:**
- Visible to entire team
- Location-specific or location-agnostic
- Never hidden
- Provide direction without spoiling solutions

### 2. **Discovery Tasks** (Trigger Level)
Tasks that reveal information and spawn new tasks.

**Examples:**
- "🔍 Examine the Safe"
- "🔍 Search the Office"
- "💬 Talk to the Janitor"
- "🔍 Investigate Security System"

**Characteristics:**
- Appear as regular tasks
- When completed → reveal information
- Trigger new tasks to appear
- Create "aha!" moments
- Often involve examining, searching, or conversing

### 3. **Spawned Tasks** (Action Level)
Specific tasks that appear after discoveries.

**Examples:**
- After examining safe → "Find 6-Digit Combination"
- After talking to janitor → "Get Coffee for Janitor"
- After searching office → "Steal Curator's Badge"

**Characteristics:**
- Hidden until triggered
- Can be team tasks or player-specific
- May have additional dependencies
- Players didn't know these existed until discovery

---

## 👥 Task Visibility Types

### **Team Tasks** (👥)
Multiple players can see and potentially complete.

**Examples:**
- "Find Vault Combination" (anyone can search for it)
- "Distract Security Guard" (anyone can attempt)
- "Collect Keys from NPCs" (different players get different keys)

**UI Indicator:** 👥 Team task badge

**Benefits:**
- Encourages collaboration
- Allows flexible role coverage
- Creates organic cooperation moments

### **Player-Specific Tasks**
Only visible to assigned player.

**Examples:**
- "Crack Safe" (Safe Cracker only)
- "Hack Security Terminal" (Hacker only)
- "Drive Getaway Car" (Driver only)

**No special indicator** (just appears in "YOUR TASKS")

**Benefits:**
- Role specialization
- Prevents crowding at one task
- Each player has unique contribution

---

## 🔄 Discovery Flow Examples

### Example 1: The Safe

**Initial State:**
```
Team Objective: 🔓 Get Into the Safe
  └─ Safe Cracker sees: 🔍 Examine the Safe
```

**After Safe Cracker examines safe:**
```
Discovery: "Vanderbilt Model 3200. Needs 6-digit combination."

New Tasks Appear:
  ├─ Team Task: 💬 Find Vault Combination (anyone)
  │   └─ Spawns at: Curator's Office, Security Room
  └─ Safe Cracker: 🎮 Crack Safe (locked until combo found)
```

**After team finds combination:**
```
Safe Cracker's task unlocks:
  └─ 🎮 Crack Safe (now available)
```

---

### Example 2: Entering Restricted Area

**Initial State:**
```
Team Objective: 💎 Steal the Diamond
  └─ Hacker sees: 🔍 Check Security System
```

**After Hacker checks system:**
```
Discovery: "Cameras active. Motion sensors on. Badge reader at door."

New Tasks Appear:
  ├─ Hacker: 🎮 Disable Cameras
  ├─ Hacker: 🎮 Loop Motion Sensors
  ├─ Team Task: 🤝 Get Security Badge (anyone)
  │   ├─ Pickpocket sees: 🎮 Steal from Guard
  │   └─ Insider sees: 💬 Convince Guard to Borrow Badge
  └─ Mastermind sees: 📋 Coordinate Entry Sequence
```

**After all security tasks done:**
```
Team Objective updates: ✅ Security Disabled → New objective appears

New Objective: 💎 Access Vault Room
  └─ Multiple paths now available
```

---

### Example 3: NPC Request Chain

**Initial State:**
```
Team Objective: 🚪 Get Past Guard
  └─ Grifter sees: 💬 Talk to Guard
```

**After Grifter talks to guard:**
```
Discovery: "Guard is hungry. Wants sandwich. Favorite: Pastrami on rye."

New Tasks Appear:
  ├─ Team Task: 🔍 Find Pastrami Sandwich
  │   └─ Driver sees: 🚗 Go to Deli (new location unlocked)
  └─ Grifter: 🤝 Give Sandwich to Guard (locked until sandwich found)
```

**After Driver goes to deli:**
```
Discovery at Deli: "Deli closed! But food truck outside."

New Task Appears:
  └─ Driver: 💬 Buy from Food Truck
      └─ NPC asks for $20
```

**After sandwich obtained:**
```
Grifter's task unlocks:
  └─ 🤝 Give Sandwich to Guard (now available)
      └─ Completes: 🚪 Get Past Guard
```

---

## 🎮 Task Types in Discovery System

### Discovery Task Types

| Icon | Type | Description | Spawns |
|------|------|-------------|--------|
| 🔍 | Examine | Inspect an object/location | Info + new tasks |
| 🔍 | Search | Look around a room | Find items + new tasks |
| 💬 | Investigate (NPC) | Ask questions | Information + requests |
| 🗣️ | Team Discussion | Coordinate findings | Unlock coordinated tasks |

### Spawned Task Types

| Icon | Type | Description | Team? |
|------|------|-------------|-------|
| 🎮 | Minigame | Interactive challenge | Can be |
| 💬 | NPC Conversation | Persuade/negotiate | Can be |
| 🤝 | Handoff | Give item to teammate | Usually |
| 🗣️ | Info Share | Tell team what you learned | Usually |
| 🔍 | Hunt | Find specific item | Can be |

---

## 🧩 Design Patterns

### Pattern 1: Progressive Revelation
Start broad, get specific through discovery.

```
Objective: "Escape the Museum"
  ↓ (discover)
Tasks: "Find exit route", "Disable alarms", "Get getaway ready"
  ↓ (discover)
Specific: "Cut wire in basement", "Steal keycard", "Park car at side entrance"
```

### Pattern 2: Branching Paths
Discovery reveals multiple solutions.

```
Objective: "Get Security Badge"
  ↓ (discover)
Branch A: Steal from guard (Pickpocket)
Branch B: Convince guard (Grifter)
Branch C: Forge fake badge (Hacker + Forger)
```

### Pattern 3: NPC Request Chains
NPCs ask for things, creating fetch quests.

```
Talk to NPC
  ↓
NPC wants item X
  ↓
Search for item X
  ↓
Find item X is in Location Y (new location)
  ↓
Go to Location Y
  ↓
Location Y has new NPC who wants item Z
  ↓
Complete chain → Original NPC gives info
```

### Pattern 4: Team Puzzle Solving
Discoveries create interdependent tasks.

```
Safe Cracker: Examine safe → Needs 3-part combination
  ↓
Spawns 3 team tasks:
  ├─ Find Part 1: Curator's Office (Insider)
  ├─ Find Part 2: Security Logs (Hacker)
  └─ Find Part 3: Hidden in Painting (anyone)
  
When all 3 found → Safe Cracker can crack safe
```

### Pattern 5: Time-Based Discovery
Some discoveries happen automatically over time.

```
Driver: Wait in car
  ↓
After 5 minutes:
Discovery: "Police scanner picks up alert!"
  ↓
New Task: Alert team to hurry
```

---

## 🛠️ Implementation for Experience Engine

### Task Structure in Generated Experience

Each task needs:

```json
{
  "task_id": "examine_safe_01",
  "type": "discovery",
  "icon": "🔍",
  "name": "Examine the Safe",
  "description": "Inspect the safe to determine what's needed to open it",
  "location": "vault_room",
  "assigned_to": "safe_cracker",
  "visibility": "role_specific",
  "dependencies": [],
  "spawns_on_complete": [
    {
      "task_id": "find_combination_01",
      "visibility": "team",
      "assigned_to": "any"
    },
    {
      "task_id": "crack_safe_01",
      "visibility": "role_specific",
      "assigned_to": "safe_cracker",
      "dependencies": ["find_combination_01"]
    }
  ],
  "discovery_result": {
    "title": "Vanderbilt Model 3200",
    "description": "This safe requires a 6-digit combination. You'll need to find it.",
    "image": "safe_closeup.jpg"
  }
}
```

### Key Fields:

- **`visibility`**: `"team"`, `"role_specific"`, `"all"`
- **`assigned_to`**: `"any"`, `"role_name"`, `["role1", "role2"]`
- **`spawns_on_complete`**: Array of task IDs that appear after this completes
- **`discovery_result`**: What the player sees when discovery happens

### Team Task Example:

```json
{
  "task_id": "find_combination_01",
  "type": "search",
  "icon": "🔍",
  "name": "Find Vault Combination",
  "description": "Search for clues about the 6-digit safe combination",
  "visibility": "team",
  "assigned_to": "any",
  "locations": ["curator_office", "security_room", "maintenance_room"],
  "can_be_completed_by": ["any"],
  "spawns_subtasks": true,
  "subtasks": [
    {
      "location": "curator_office",
      "description": "Found first 2 digits: 47",
      "completes_part": "1_of_3"
    },
    {
      "location": "security_room", 
      "description": "Found middle 2 digits: 32",
      "completes_part": "2_of_3"
    },
    {
      "location": "maintenance_room",
      "description": "Found last 2 digits: 89",
      "completes_part": "3_of_3"
    }
  ]
}
```

---

## 📱 Real-Time Updates

### When Discovery Happens:

**Player who discovered:**
1. Sees discovery result screen
2. New tasks appear in their task list
3. Returns to game screen

**Other team members:**
1. Notification: "🔍 [Player] made a discovery!"
2. New team tasks appear in their lists
3. Objective status updates

### WebSocket Events:

```javascript
// Player completes discovery task
{
  "event": "task_completed",
  "task_id": "examine_safe_01",
  "player_id": "player_123",
  "spawns_tasks": true
}

// Server broadcasts to team
{
  "event": "discovery_made",
  "by_player": "Alex (Safe Cracker)",
  "discovery": "Found safe requires 6-digit combination",
  "new_tasks": [
    {
      "task_id": "find_combination_01",
      "visible_to": "all",
      "name": "Find Vault Combination"
    }
  ]
}

// Each client updates their UI
- Shows notification
- Adds new tasks to available list
- Updates objective progress
```

---

## 🎨 UI Elements for Discovery

### Task Indicators:

- **🔍 Discovery task** → Light bulb animation when tapped
- **👥 Team task** → Badge showing "Team can help"
- **🔒 Locked task** → (Not shown until available)
- **✨ Just unlocked** → Sparkle animation for 5 seconds

### Notifications:

```
┌─────────────────────────────────┐
│  🔍 ALEX MADE A DISCOVERY!      │
│                                 │
│  "Found safe requires           │
│   combination"                  │
│                                 │
│  ✨ New tasks available          │
└─────────────────────────────────┘
```

### Objective Progress:

```
Team Objective: 🔓 Get Into the Safe
  ✅ Examined safe
  ⏳ Finding combination (2/3 found)
  🔒 Crack safe (waiting for combination)
```

---

## 🎯 Benefits of This System

### For Players:
1. **Mystery** - Don't see everything upfront
2. **Discovery** - "Aha!" moments when finding clues
3. **Teamwork** - Share discoveries with team
4. **Flexibility** - Multiple paths to solve problems
5. **Replayability** - Different discoveries each time

### For Game Design:
1. **Narrative** - Story unfolds naturally
2. **Pacing** - Control information flow
3. **Complexity** - Hide complexity until needed
4. **Adaptability** - Generate different paths per playthrough
5. **Engagement** - Players actively explore vs following checklist

### For Experience Engine:
1. **Variation** - Generate different discovery sequences
2. **Branching** - Create multiple solution paths
3. **Difficulty** - Control how obvious clues are
4. **NPC Integration** - NPCs provide discovery moments
5. **Replayability** - Randomize what's discovered where

---

## 📝 Guidelines for Experience Generation

### DO:
✅ Start with 1-3 clear team objectives  
✅ Create discovery tasks that feel natural (examine, search, ask)  
✅ Make some tasks team-visible, some role-specific  
✅ Chain discoveries (one leads to another)  
✅ Provide multiple paths when possible  
✅ Use NPC conversations as discovery moments  
✅ Hide 60-70% of tasks until triggered  

### DON'T:
❌ Show entire dependency tree upfront  
❌ Make every task player-specific (too isolating)  
❌ Create linear-only paths (no discovery, just sequence)  
❌ Overwhelm with too many team objectives at start  
❌ Make discoveries too obscure (players should have direction)  
❌ Forget location requirements for discovery  

---

## 🔮 Future Enhancements

### Phase 2:
- **Time-based discoveries** (wait 5 min → new info)
- **Conditional discoveries** (if X happens, discover Y)
- **Failed discovery paths** (wrong assumption leads to dead end)

### Phase 3:
- **Player-created tasks** (mark location for team)
- **Dynamic objectives** (objectives change based on discoveries)
- **Secret discoveries** (optional side content)

### Phase 4:
- **AI-generated discoveries** (LLM creates discovery text on-the-fly)
- **Procedural puzzles** (combination/clues generated per game)
- **Adaptive difficulty** (more/fewer hints based on team progress)

---

## 📊 Example Full Game Flow

```
GAME START

Team Objective: 💎 Steal the Museum Diamond

Initial Tasks:
  Mastermind: 📋 Scout the Museum
  Hacker: 🔍 Check Security System
  Insider: 💬 Talk to Curator
  Safe Cracker: 🔍 Examine Vault
  Driver: 🚗 Park Getaway Car

↓ (Players complete discoveries)

AFTER DISCOVERIES

Team Objective: 💎 Steal the Museum Diamond

Discovered Information:
  • Diamond is in vault (Safe Cracker examined)
  • Vault needs 3-part code (Safe Cracker examined)
  • Security has cameras + motion sensors (Hacker checked)
  • Curator knows part of code (Insider talked)
  • Gala event tonight - good timing (Mastermind scouted)

New Available Tasks:
  Team: 🔍 Find Code Part 1 (Curator's Office)
  Team: 🔍 Find Code Part 2 (Security Logs)
  Team: 🔍 Find Code Part 3 (Hidden Somewhere)
  Hacker: 🎮 Disable Cameras
  Hacker: 🎮 Loop Motion Sensors
  Grifter: 💬 Distract Guards During Gala
  Insider: 🤝 Get Curator to Reveal Code Part

↓ (Players complete tasks)

APPROACHING FINALE

Team Objective: 💎 Steal the Museum Diamond (85% complete)

All Security Disabled ✅
All Code Parts Found ✅

Final Tasks:
  Safe Cracker: 🎮 Crack Vault (NOW AVAILABLE!)
  Team: 🤝 Extract Diamond to Driver
  Driver: 🚗 Execute Getaway

↓

HEIST COMPLETE! 🎉
```

---

## 🎬 Conclusion

The **Discovery System** transforms The Heist from a linear task list into a dynamic, emergent experience. Players start with direction but discover the details through exploration, creating memorable "aha!" moments and genuine teamwork.

**Key Takeaway:** Show the destination, hide the path, let players discover the journey.

