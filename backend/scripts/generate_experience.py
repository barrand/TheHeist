#!/usr/bin/env python3
"""
Generate a complete heist experience for a scenario using Gemini AI.

Usage:
    python generate_experience.py --scenario museum_gala_vault --roles mastermind hacker safe_cracker
    python generate_experience.py --scenario train_robbery_car --roles mastermind muscle cat_burglar --output custom_heist.md
"""

import argparse
import json
import sys
from pathlib import Path
from google import genai
from config import GEMINI_API_KEY, GEMINI_EXPERIENCE_MODEL, DATA_DIR, DESIGN_DIR, EXAMPLES_DIR


def load_json(file_path):
    """Load and return JSON data from file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def load_text(file_path):
    """Load and return text content from file."""
    with open(file_path, 'r') as f:
        return f.read()


def get_scenario(scenario_id, scenarios_data):
    """Get scenario details by ID."""
    for scenario in scenarios_data['scenarios']:
        if scenario['scenario_id'] == scenario_id:
            return scenario
    return None


def get_role_details(role_ids, roles_data):
    """Get details for specified roles."""
    role_details = []
    for role in roles_data['roles']:
        if role['role_id'] in role_ids:
            role_details.append(role)
    return role_details


def build_prompt(scenario, roles, design_guide, npc_guide, example):
    """Build the prompt for Gemini to generate a heist experience file."""
    
    role_names = [role['name'] for role in roles]
    role_list = ', '.join(role_names)
    
    # Build role minigames reference
    role_minigames = []
    for role in roles:
        minigames = [f"  - {mg['id']}: {mg['description']}" for mg in role.get('minigames', [])]
        if minigames:
            role_minigames.append(f"**{role['name']}**:\n" + '\n'.join(minigames))
        else:
            role_minigames.append(f"**{role['name']}**: No minigames (coordination only)")
    
    minigames_section = '\n\n'.join(role_minigames)
    
    prompt = f"""You are an expert game designer creating an experience file for a collaborative heist game.

## Your Task

Generate a complete experience file with a **task dependency system** for this heist scenario.

**Scenario**: {scenario['name']} (ID: {scenario['scenario_id']})
**Objective**: {scenario['objective']}
**Summary**: {scenario['summary']}
**Selected Roles**: {role_list}
**Player Count**: {len(roles)} players

## Available Minigames by Role

{minigames_section}

## 🔴 CRITICAL: GENERATION WORKFLOW (FOLLOW THIS ORDER!)

To avoid validation errors, you MUST generate content in this exact order:

**STEP 1: Define ALL Locations**
- Create 6-9 locations for {len(roles)} players
- Give each location a clear `ID` in snake_case format
- Write them in the ## Locations section

**STEP 2: Define ALL NPCs with their outcomes**
- For each NPC, define exactly ONE outcome in Information Known or Actions Available
- Give each outcome a clear `ID` in snake_case format
- Write them in the ## NPCs section
- **REMEMBER THE OUTCOME IDs YOU CREATE!** You'll need them in Step 4.

**STEP 3: Define ALL Items**
- Give each item a clear `ID` in snake_case format
- If item is Hidden: true, it MUST have **Unlock** prerequisites
- Write them under location headers in ## Items by Location section

**STEP 4: Create Tasks that reference ONLY the IDs from Steps 1-3**
- Task locations: ONLY use location IDs from Step 1 (in backticks: `location_id`)
- Task NPCs: ONLY use NPC IDs from Step 2 (in backticks: `npc_id`)
- Task Target Outcomes: ONLY use outcome IDs from Step 2 (in backticks: `outcome_id`)
- Task Prerequisites: ONLY use IDs from Steps 1-4 (Task/Outcome/Item `id`)
- **NEVER invent new IDs in Step 4 that weren't defined in Steps 1-3!**

**BEFORE YOU FINISH:**
- Review ALL task locations and verify each one exists in ## Locations
- Review ALL task NPCs and verify each one exists in ## NPCs
- Review ALL task target outcomes and verify they match the NPC's outcome
- Review ALL hidden items and verify they have unlock conditions

## Design Guidelines

{design_guide}

## NPC Personality Guidelines

{npc_guide}

## Example Experience File

Here's an example of the format and quality expected:

{example}

## CRITICAL: ID-ONLY REFERENCE FORMAT

**THIS IS THE #1 CAUSE OF VALIDATION FAILURES!**

When writing tasks, you MUST use backtick IDs for ALL references:

❌ WRONG:
```
- *Location:* Safe House
- *Location:* Bank Lobby  
- *NPC:* `lobby_guard` (without backticks on location!)
```

✅ CORRECT:
```
- *Location:* `safe_house`
- *Location:* `bank_lobby`
- *NPC:* `lobby_guard` (Guard Name)
```

**MEMORIZE THIS:**
- Location in tasks = `location_id` in backticks
- NPC in tasks = `npc_id` in backticks
- Prerequisites = `task_id`, `outcome_id`, `item_id` in backticks
- NEVER use the display Name, ALWAYS use the ID

---

## VALIDATION REQUIREMENTS (MUST FOLLOW)

Your generated scenario MUST pass these validation rules:

### Location Count (CRITICAL)
- **2-3 players**: 4-6 locations minimum
- **4-5 players**: 6-9 locations minimum  
- **6-8 players**: 8-12 locations minimum
- **9-12 players**: 10-15 locations minimum
Include: preparation locations, entry points, public areas, restricted areas, target location, escape routes.

**🔴 CRITICAL LOCATION WORKFLOW:**

**STEP 1: Define ALL locations FIRST in ## Locations section**
```markdown
## Locations

### Safe House (Starting Location)
- **ID**: `safe_house`
- **Name**: Safe House
- **Description**: ...

### Bank Lobby
- **ID**: `bank_lobby`
- **Name**: Bank Lobby
- **Description**: ...
```

**STEP 2: In tasks, ONLY reference location IDs that you defined in STEP 1**
```markdown
**H1. 💬 NPC_LLM** - Talk to Guard
- *Location:* `bank_lobby`  ← MUST match a location ID from Locations section!
```

**❌ COMMON MISTAKES:**
1. Task references location `parking_garage` but Locations section only has `parking_lot` ← WRONG! ID doesn't match!
2. Task references location `Bank Lobby` (name) instead of `bank_lobby` (ID) ← WRONG! Must use ID!
3. Forgetting to define a location in Locations section ← WRONG! Define ALL locations first!

**✅ VALIDATION CHECKLIST:**
1. List ALL location IDs from ## Locations section
2. For EACH task, verify the Location field uses an ID from that list (in backticks)

### Task Count (CRITICAL)
- **3-7 players**: 30-40 tasks total
- **8-12 players**: 40-50 tasks total
Distribute evenly: each role should have 3-8 tasks.

### Cross-Role Interaction (CRITICAL)
- Include at least **3 handoff tasks** (🤝 HANDOFF) where items are physically transferred
- Include at least **2 info share tasks** (🗣️ INFO) where players verbally coordinate
- Include **6-10 search tasks** (🔍 SEARCH) for item discovery

### Task Balance (CRITICAL)
- **60-70% social interactions**: NPC conversations, handoffs, info shares, searches
- **30-40% minigames**: Action tasks
- Do NOT make every task a minigame!

### Reference Integrity (CRITICAL - USE IDS ONLY!)

**MANDATORY ID-ONLY REFERENCE RULES:**

1. **Task Locations** - MUST use location ID in backticks:
   ```
   - *Location:* `bank_lobby`     ✅ CORRECT
   - *Location:* Bank Lobby       ❌ WRONG (no backticks, uses Name)
   - *Location:* bank_lobby       ❌ WRONG (no backticks)
   ```

2. **Task NPCs** - MUST use NPC ID in backticks:
   ```
   - *NPC:* `lobby_guard_brenda` (Guard Name)    ✅ CORRECT
   - *NPC:* lobby_guard_brenda                   ❌ WRONG (no backticks)
   - *NPC:* Brenda Jenkins                       ❌ WRONG (uses name)
   ```

3. **Prerequisites** - MUST use IDs in backticks:
   ```
   - Task `MM1`             ✅ CORRECT
   - Task MM1               ❌ WRONG
   - Item `keycard`         ✅ CORRECT
   - Outcome `guard_info`   ✅ CORRECT
   ```

4. **Target Outcomes** - MUST use outcome ID in backticks:
   ```
   - *Target Outcomes:* `guard_distracted`   ✅ CORRECT
   ```

**VERIFICATION CHECKLIST:**
- [ ] Every task location uses `location_id` format
- [ ] Every task NPC uses `npc_id` format  
- [ ] Every prerequisite uses `id` format
- [ ] Every NPC ID exists in NPCs section
- [ ] Every outcome ID exists in an NPC's "Information Known"
- [ ] Every item ID exists in Items section
- [ ] Every location ID exists in Locations section

### Task IDs (CRITICAL)
- Use proper format: `MM1`, `MM2` for Mastermind, `H1`, `H2` for Hacker, etc.
- Role codes: MM=Mastermind, H=Hacker, SC=Safe Cracker, D=Driver, I=Insider, G=Grifter, M=Muscle, L=Lookout, F=Fence, CB=Cat Burglar, CL=Cleaner, PP=Pickpocket
- Number sequentially starting from 1

---

## CRITICAL: Task System Requirements

### 1. Team Objectives (1-3 high-level goals)
Start with clear objectives visible to ALL players:
- ✅ Example: "🔓 Get Into the Safe"
- ✅ Example: "💎 Steal the Diamond" 
- ✅ Example: "🚪 Escape the Building"
- Keep them action-oriented and clear

### 2. Task Types
Every task MUST be one of these types (using the matching emoji):
- 🎮 **Minigame**: Player-controlled action (e.g., dial_rotation, wire_connecting)
- 💬 **NPC_LLM**: Dialogue or interaction with **AI-controlled NPCs ONLY**
- 🔍 **Search**: Player searches a location for items
- 🤝 **Handoff**: Physical item transfer between players (tracked in inventory)
- 🗣️ **Info Share**: Verbal information exchange between players (real-life conversation)

**No other task types are allowed.** Every task a player sees must have a clear way to complete it:
- Minigame → play the minigame
- NPC_LLM → talk to an **AI NPC** and achieve the outcome
- Search → go to the location and search for items
- Handoff → transfer an item to another player
- Info Share → tell another player the information, then confirm shared

⚠️ **CRITICAL DISTINCTION: NPCs vs Players**
- **NPCs** = AI-controlled characters (guards, staff, civilians) that players talk to using the conversation system
- **Players** = Human players with assigned roles (Mastermind, Hacker, etc.)
- **NEVER create "Player NPCs"!** Players talking to each other = 🗣️ **INFO_SHARE**, NOT 💬 NPC_LLM
- **NPC_LLM is ONLY for AI NPCs**, not for player-to-player communication!

Examples:
- ✅ CORRECT: "Talk to the Security Guard" → 💬 NPC_LLM (AI character)
- ✅ CORRECT: "Brief the Safe Cracker about the plan" → 🗣️ INFO_SHARE (player-to-player)
- ❌ WRONG: "Talk to the Safe Cracker player" → NPC_LLM (players are NOT NPCs!)

**Do NOT create tasks that are just "go to a location."** If a player needs to be somewhere, make it a prerequisite on the task they'll do there.

### 3. Task Design Principles

**PRINCIPLES:**
1. **Every task needs a clear player action** - The player must DO something to complete it
2. **Use prerequisites for gating** - Don't create placeholder tasks just to block progress; use Task/Outcome/Item prerequisites
3. **NPC interactions should feel natural** - NPCs have personality, not just info to dump
4. **Vary the task types** - Mix NPC conversations, searches, minigames, and coordination
5. **Player agency** - Give players choices in how they approach objectives

**Make NPCs feel real, not just info dispensers:**
- Give them wants, needs, problems, quirks
- Let conversations flow naturally, not just Q&A
- Have them reveal info through personality, not exposition dumps
- Make players work to get information (build trust, solve problems, trade favors)

### 4. Team vs Player-Specific Tasks

**Player-Specific Tasks** - Only one role can do:
- "Crack Safe" (Safe Cracker only)
- "Hack Terminal" (Hacker only)

**Cross-role coordination** happens through:
- 🗣️ Info Share tasks (one player tells another what they learned)
- 🤝 Handoff tasks (one player gives another an item they need)
- Outcome prerequisites (one player's NPC success unlocks another player's task)

## NPC Conversation System Format (CRITICAL!)

⚠️ **NPCs are AI-CONTROLLED CHARACTERS ONLY!**
- Create NPCs for: guards, staff, civilians, officials, bystanders
- **NEVER create NPCs for player roles!** Players (Mastermind, Hacker, etc.) are NOT NPCs!
- Players communicate via 🗣️ INFO_SHARE tasks, NOT NPC_LLM tasks!

Each NPC MUST include structured data for the conversation system:

### NPC Format:
```markdown
### Role Title - NPC Name
- **ID**: `snake_case_id`
- **Role**: Their job/role
- **Location**: Where they are
- **Age**: number
- **Gender**: male/female
- **Ethnicity**: description
- **Clothing**: what they wear
- **Expression**: facial expression
- **Attitude**: personality vibe
- **Details**: props/visual details
- **Personality**: Detailed personality for LLM conversations (2-3 sentences)
- **Relationships**: How this NPC relates to other NPCs in the scenario (who they know, what they think of them). This adds natural conversational depth — they might mention other NPCs organically.
- **Story Context**: Ground-truth facts about the world this NPC knows. Prevents the AI from improvising contradictions. Include: where key objects actually are, what the NPC would/wouldn't do, what is and isn't public knowledge. (2-4 sentences)
- **Information Known**:
  - `info_id` HIGH: The ONE piece of info this NPC provides (tagged with ID)
  - LOW: Flavor text they might share (no ID = not tracked, just conversation filler)
  - LOW: More flavor to make the NPC feel real
- **Actions Available**:
  - (none, if this NPC provides info instead of an action)
  - OR: `action_id` HIGH: The ONE action this NPC can perform (if action-type NPC)
- **Cover Story Options**:
  - `cover_id`: "What the player claims to be" -- (how the NPC feels about this person)
  - `another_cover`: "Another plausible cover story" -- (NPC's instinct about this person)
  - `funny_cover`: "Something silly/absurd/funny" -- (NPC's bewildered reaction)
```

Rules for NPCs:
- ONE outcome per NPC: each NPC has exactly ONE tagged info item OR ONE action (not both, not multiple). This is their sole purpose in the story.
- Additional LOW items (no ID) can be added as flavor to make conversation natural, but only ONE item has an ID.
- Each NPC needs exactly 3 cover story options: 2 plausible covers and 1 silly/funny/offbeat option that would make a player laugh. No trust labels -- just the cover description and the NPC's natural reaction in parentheses.
- Info/Action IDs must be snake_case and unique across the experience
- Every NPC must be targeted by exactly one task with a matching Target Outcome
- If you need more outcomes, add more NPCs -- don't overload one NPC
- NARRATIVE CONSISTENCY (Story Context): Every NPC MUST have a Story Context field with immutable world facts. This prevents the AI playing the NPC from improvising contradictions (e.g., saying stolen items are "on display" when they're in a locked vault). Think carefully about: where key objects physically are and why, what is public vs secret knowledge, what this NPC would and would NOT volunteer to do, and how the scenario's setup constrains the NPC's behavior.

**🔴 CRITICAL NPC-TO-TASK MATCHING WORKFLOW:**

When creating NPCs and tasks, you MUST follow this exact workflow:

**STEP 1: Define NPC with outcome**
```markdown
### Security Guard - Officer Mike
- **ID**: `security_guard_mike`
- **Information Known**:
  - `camera_feeds_info` HIGH: Location of blind spots in camera coverage
```

**STEP 2: Create task that EXACTLY matches the outcome**
```markdown
**H1. 💬 NPC_LLM** - Get Camera Info from Guard
- *NPC:* `security_guard_mike` (Officer Mike)
- *Target Outcomes:* `camera_feeds_info`  ← MUST MATCH NPC'S OUTCOME ID EXACTLY!
```

**❌ COMMON MISTAKES TO AVOID:**
1. NPC provides `camera_feeds_info` but task wants `guard_distracted` ← WRONG! Outcomes don't match!
2. Task references NPC `informant_joe` but no NPC with that ID exists ← WRONG! NPC doesn't exist!
3. Task D5 requires outcome `all_clear_signal` but no NPC provides it ← WRONG! Outcome doesn't exist!

**✅ VALIDATION CHECKLIST BEFORE FINISHING:**
1. List ALL outcome IDs from ALL NPCs (from Information Known and Actions Available)
2. For EACH NPC task, verify the Target Outcome exists in that NPC's definition
3. For EACH task prerequisite of type Outcome, verify it exists in SOME NPC's definition
4. For EACH NPC, verify exactly ONE task references it with matching Target Outcome

### Task Format (ID-ONLY REFERENCES):
```markdown
1. **MM1. 💬 NPC_LLM** - Task Description
   - *Description:* Detailed description
   - *NPC:* `npc_id` (NPC Name)
   - *Target Outcomes:* `single_outcome_id`
   - *Location:* `location_id`
   - *Prerequisites:* None (starting task)

2. **MM2. 🎮 minigame_id** - Task Description
   - *Description:* Detailed description
   - *Location:* `location_id`
   - *Prerequisites:*
     - Task `MM1` (description of why)
     - Outcome `info_id` (what info is needed)
     - Item `item_id` (what item is needed)
```

CRITICAL: Notice Location uses `location_id` in backticks, NOT "Location Name"!

Rules for Tasks:
- **ALWAYS use backtick IDs for ALL references**: `location_id`, `npc_id`, `item_id`, `outcome_id`
- Use typed prerequisites: `Task`, `Outcome`, `Item` (not plain dependency IDs)
- NPC tasks MUST have `*Target Outcomes:*` with exactly ONE outcome ID
- Task location format: `*Location:* \`location_id\``
- Task NPC format: `*NPC:* \`npc_id\` (Display Name)`
- Search tasks use `*Search Items:*` with item IDs: `item_1`, `item_2`
- Any player role can do search/social tasks; role-locked tasks are minigames

### Item Format:
```markdown
### Location Name
- **ID**: `snake_case_id`
  - **Name**: Display Name
  - **Description**: What the item is
  - **Visual**: Detailed visual description for image generation
  - **Required For**: Task ID or objective description
  - **Hidden**: false
  - **Unlock**:
    - Task `SC2` (vault must be cracked first)
```

Rules for Items:
- Every item needs an ID, Name, Description, and Visual field
- Use `**Unlock**` to gate items behind prerequisites (same format as task prerequisites: Task, Outcome, Item)
- Items without `**Unlock**` are always visible when a player searches that location
- Use Unlock when an item should only appear AFTER something happens (e.g., jewels appear after vault is cracked, a key appears after a guard leaves)
- The `**Hidden**` field is for items that require a thorough search to find (separate from unlock gating)

**🔴 CRITICAL HIDDEN ITEM RULE:**

**IF an item has `Hidden: true`, it MUST have `**Unlock**` prerequisites!**

❌ WRONG - This item is IMPOSSIBLE to find:
```markdown
- **ID**: `secret_document`
  - **Hidden**: true
  - **Unlock**:  ← NO UNLOCK! Item can NEVER be found!
    - None
```

✅ CORRECT - Hidden item with unlock:
```markdown
- **ID**: `secret_document`
  - **Hidden**: true
  - **Unlock**:
    - Task `H1` (hack security first)
    - Outcome `safe_opened` (safe must be open)
```

✅ CORRECT - Non-hidden item (no unlock needed):
```markdown
- **ID**: `security_badge`
  - **Hidden**: false  ← Available immediately when player searches
```

**Rule:** Hidden: true + No Unlock = BROKEN SCENARIO (item is unfindable)

## Standard Requirements

1. **Follow the markdown format** shown in the example (structure, not content!)
2. **Use only minigames** listed above for each role
3. **Include NPC personalities** - Make each one memorable and unique!
4. **Add 🔍 Search tasks** for room inventory mechanics (6-10 search tasks)
5. **Target 60-70% social interactions** (NPC + Search + Handoffs + Info shares)
6. **Create 3-5 critical tasks per role** with clear dependencies
7. **Include location list** at the beginning (12-18 locations)
8. **Add generation header** showing scenario, roles, and player count
9. **Generate both full and simplified Mermaid diagrams**
10. **Use typed prerequisites** on all tasks (Task, Outcome, Item)
11. **Include cover story options** for every NPC (2 plausible + 1 funny, with NPC reaction)
12. **Tag all NPC info** with snake_case IDs for outcome tracking
13. **Include Story Context** for every NPC — ground-truth facts that prevent narrative contradictions

## CREATIVITY GUIDELINES ⭐

**BE CREATIVE! Don't copy the examples directly:**
- Make each NPC distinct with different problems and personalities
- Think about what would be fun and surprising for players
- Create organic task chains that feel natural to the scenario
- Allow multiple valid approaches when it makes sense
- Vary task types: mix NPC conversations, searches, minigames, info shares, and handoffs

**Think about the scenario:**
- Museum heist? Think about art, security systems, gala events, curators, collectors
- Train robbery? Think about schedules, conductors, passengers, cargo, stations
- Bank job? Think about vaults, managers, security protocols, customers, routines

**Make each experience feel fresh and replayable!**

## Output Format

Generate a complete markdown file with:
- Generation header with scenario/role info
- Scenario overview
- Locations list (organized by category)
- Task types legend (only: Minigame, NPC_LLM, Search, Handoff, Info Share)
- Items by Location
- NPCs section with full personality data
- Roles & Tasks (detailed task list for each role with typed prerequisites)
- Dependency tree diagrams (Mermaid)
- Story Flow summary

**Important**: 
- Every task must have a *Location:* field
- Every NPC must have structured personality data (see NPC Format above)
- Search tasks must specify `*Search Items:*`
- NPC tasks must specify `*NPC:*` and `*Target Outcomes:*`
- Follow dependencies logically (can't crack safe before examining it)
- Make it fun and replayable with quirky NPCs!

**CRITICAL - Mermaid Diagram Rules**:
- Node IDs MUST be simple: `MM1`, `H2`, `SC3`, `I4` (letters + numbers ONLY)
- NEVER use underscores in node IDs: `MM1_S` ❌ BAD, `MM1` ✅ GOOD
- NEVER use special characters in node IDs: `SC2_H` ❌ BAD, `SC2` ✅ GOOD
- Colons ARE allowed in labels: `{{🎮 wire_connecting: Prep Device}}` ✅ GOOD
- Use square brackets for handoffs: `MM1[🤝 DEVICE to Hacker]`
- Use double curly braces for tasks: `H2{{💬 Hacker: Disable System}}`
- Example CORRECT: `START --> MM1{{💬 MM: Brief Crew}}`
- Example WRONG: `START --> MM1_C{{💬 MM: Brief Crew}}` (underscore breaks parser!)
- Study the example Mermaid diagrams carefully and copy that exact style

## CONCRETE EXAMPLES: Task Chain Patterns

Show variety! Here are different patterns to inspire you (don't copy exactly, create your own):

### EXAMPLE 1: NPC → Info Share → Minigame Chain
```markdown
1. **MM1. 💬 NPC_LLM** - Learn Vault Location from Curator
   - *Description:* Chat with the curator to learn where the jewels are kept.
   - *NPC:* `curator` (Dr. Elena Vasquez)
   - *Target Outcomes:* `vault_location`
   - *Location:* Grand Hall
   - *Prerequisites:* None (starting task)

2. **MM2. 🗣️ INFO** - Share Intel with Safe Cracker
   - *Description:* Radio the Safe Cracker with the vault's location and guard schedule.
   - *Location:* Any (radio communication)
   - *Prerequisites:*
     - Task `MM1` (learned vault location)

3. **SC1. 🎮 dial_rotation** - Crack the Vault Lock
   - *Description:* Use your tools to crack the vault combination.
   - *Location:* Vault Room
   - *Prerequisites:*
     - Task `MM2` (received intel from Mastermind)
     - Item `safe_cracking_tools` (need tools)
```

### EXAMPLE 2: Search → NPC → Handoff Chain
```markdown
1. **H1. 🔍 SEARCH** - Find Security Badge
   - *Description:* Search the break room for a security badge.
   - *Search Items:* security_badge
   - *Location:* Break Room
   - *Prerequisites:* None (starting task)

2. **H2. 💬 NPC_LLM** - Convince Guard to Take a Break
   - *Description:* Get the guard to step away from his post.
   - *NPC:* `guard` (Officer Mike)
   - *Target Outcomes:* `leave_post`
   - *Location:* Hallway
   - *Prerequisites:*
     - Item `security_badge` (need badge to look official)

3. **H3. 🤝 HANDOFF** - Give Badge to Insider
   - *Description:* Hand the security badge to the Insider who needs it to access the server room.
   - *Handoff Item:* security_badge
   - *Handoff To:* Insider
   - *Prerequisites:*
     - Outcome `leave_post` (guard is gone, safe to exchange)
```

**IMPORTANT REMINDERS:**
- Be creative! Don't copy these examples directly
- Every task must have a clear player action (search, talk, play minigame, share info, hand off item)
- Create organic chains where tasks lead naturally to next steps
- Make players feel clever for connecting information
- Allow multiple valid approaches when possible

Now generate a complete, varied experience file for the scenario above.
"""
    
    return prompt


def generate_experience(scenario_id, role_ids, output_file=None):
    """Generate complete heist experience using Gemini AI."""
    
    print(f"🎮 Generating heist experience...")
    print(f"   Scenario: {scenario_id}")
    print(f"   Roles: {', '.join(role_ids)}")
    print(f"   Model: {GEMINI_EXPERIENCE_MODEL}")
    print()
    
    # Load data files
    print("📂 Loading data files...")
    scenarios = load_json(DATA_DIR / 'scenarios.json')
    roles = load_json(DATA_DIR / 'roles.json')
    design_guide = load_text(DESIGN_DIR / 'dependency_tree_design_guide.md')
    npc_guide = load_text(DESIGN_DIR / 'npc_personalities_guide.md')
    example = load_text(EXAMPLES_DIR / 'museum_gala_dependency_tree.md')
    
    # Get scenario and role details
    scenario = get_scenario(scenario_id, scenarios)
    if not scenario:
        print(f"❌ Error: Scenario '{scenario_id}' not found")
        sys.exit(1)
    
    selected_roles = get_role_details(role_ids, roles)
    if len(selected_roles) != len(role_ids):
        found_ids = [r['role_id'] for r in selected_roles]
        missing = set(role_ids) - set(found_ids)
        print(f"❌ Error: Roles not found: {missing}")
        sys.exit(1)
    
    print(f"✓ Loaded scenario: {scenario['name']}")
    print(f"✓ Loaded {len(selected_roles)} roles")
    print()
    
    # Build prompt
    print("🤖 Building prompt...")
    prompt = build_prompt(scenario, selected_roles, design_guide, npc_guide, example)
    
    # Estimate token count (rough)
    estimated_tokens = len(prompt.split()) * 1.3  # rough estimate
    print(f"✓ Prompt built (~{int(estimated_tokens/1000)}K tokens)")
    print()
    
    # Call Gemini API
    print(f"🚀 Calling Gemini API ({GEMINI_EXPERIENCE_MODEL})...")
    print("   This may take 30-60 seconds...")
    print()
    
    try:
        # Initialize client with new SDK
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Generate content using new SDK
        response = client.models.generate_content(
            model=GEMINI_EXPERIENCE_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=32000,
            )
        )
        
        if not response.text:
            print("❌ Error: No response from Gemini")
            sys.exit(1)
        
        result = response.text
        print(f"✅ Generated {len(result.split())} words")
        print()
        
        # Save to file
        if output_file:
            output_path = Path(output_file)
        else:
            # Default: scripts/output/{scenario_id}_{roles}.md
            roles_str = '_'.join(role_ids[:3])  # First 3 roles
            if len(role_ids) > 3:
                roles_str += f'_plus{len(role_ids)-3}'
            output_path = Path('scripts/output') / f"{scenario_id}_{roles_str}.md"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result)
        
        print(f"💾 Saved to: {output_path}")
        print()
        print("✨ Done!")
        
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        sys.exit(1)


def generate_experience_multistage(scenario_id, role_ids, output_file=None):
    """
    Generate experience using multi-stage pipeline
    
    Pipeline:
    1. Story Generation - LLM creates semi-structured story
    2. Structure Extraction - Parse story to JSON graph
    3. Validation & Fixing - Validate and auto-fix graph
    4. Markdown Rendering - Convert graph to final markdown
    
    Args:
        scenario_id: Scenario ID
        role_ids: List of role IDs
        output_file: Output path (optional)
    
    Returns:
        Path to generated markdown file
    """
    print(f"🚀 Multi-Stage Generation Pipeline")
    print(f"={'='*60}")
    print(f"Scenario: {scenario_id}")
    print(f"Roles: {', '.join(role_ids)}")
    print(f"{'='*60}\n")
    
    # Import stage modules
    sys.path.insert(0, str(Path(__file__).parent / 'generators'))
    from generators.story_generator import generate_story
    from generators.structure_extractor import extract_structure
    from generators.graph_validator_fixer import validate_and_fix_graph
    from generators.markdown_renderer import render_markdown
    
    # Stage 1: Generate story
    print(f"📖 Stage 1: Story Generation")
    print(f"-" * 60)
    story = generate_story(
        scenario_id=scenario_id,
        role_ids=role_ids,
        api_key=GEMINI_API_KEY,
        model=GEMINI_EXPERIENCE_MODEL,
        data_dir=DATA_DIR
    )
    print(f"✅ Generated story ({len(story.split())} words)\n")
    
    # Save story for debugging
    story_path = Path('output/stories') / f"{scenario_id}_{'_'.join(role_ids[:2])}_story.txt"
    story_path.parent.mkdir(parents=True, exist_ok=True)
    story_path.write_text(story)
    print(f"💾 Story saved to: {story_path}\n")
    
    # Stage 2: Extract structure
    print(f"📊 Stage 2: Structure Extraction")
    print(f"-" * 60)
    graph = extract_structure(story, scenario_id, role_ids)
    print(f"✅ Extracted structure:")
    print(f"   - {len(graph.locations)} locations")
    print(f"   - {len(graph.items)} items")
    print(f"   - {len(graph.npcs)} NPCs")
    print(f"   - {len(graph.tasks)} tasks\n")
    
    # Stage 3: Validate and fix
    print(f"🔧 Stage 3: Validation & Fixing")
    print(f"-" * 60)
    fixed_graph, validation_result = validate_and_fix_graph(graph, max_iterations=5)
    
    if not validation_result.is_valid:
        print(f"\n❌ Validation failed after fixes:")
        for error in validation_result.errors:
            print(f"   - {error}")
        raise RuntimeError("Failed to generate valid scenario")
    
    if validation_result.fixes_applied:
        print(f"✅ Applied {len(validation_result.fixes_applied)} fixes\n")
    else:
        print(f"✅ No fixes needed\n")
    
    # Stage 4: Render markdown
    print(f"📝 Stage 4: Markdown Rendering")
    print(f"-" * 60)
    markdown = render_markdown(fixed_graph)
    print(f"✅ Rendered markdown ({len(markdown.split())} words)\n")
    
    # Save final output
    if output_file:
        output_path = Path(output_file)
    else:
        roles_str = '_'.join(role_ids[:3])
        if len(role_ids) > 3:
            roles_str += f'_plus{len(role_ids)-3}'
        output_path = Path('backend/scripts/output') / f"{scenario_id}_{roles_str}.md"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown)
    
    print(f"{'='*60}")
    print(f"✅ Multi-stage generation complete!")
    print(f"💾 Saved to: {output_path}")
    print(f"{'='*60}\n")
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Generate a complete heist experience for a scenario',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_experience.py --scenario museum_gala_vault --roles mastermind hacker safe_cracker
  python generate_experience.py --scenario train_robbery_car --roles mastermind muscle cat_burglar driver
  python generate_experience.py --scenario museum_gala_vault --roles mastermind fence hacker insider --output backend/experiences/my_heist.md
  python generate_experience.py --scenario museum_gala_vault --roles mastermind hacker --legacy  (use old single-stage)
        """
    )
    
    parser.add_argument(
        '--scenario',
        required=True,
        help='Scenario ID (e.g., museum_gala_vault, train_robbery_car)'
    )
    
    parser.add_argument(
        '--roles',
        nargs='+',
        required=True,
        help='Role IDs (e.g., mastermind hacker safe_cracker)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path (default: scripts/output/{scenario}_{roles}.md)'
    )
    
    parser.add_argument(
        '--legacy',
        action='store_true',
        help='Use legacy single-stage generation (for comparison)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run validation checks after generation'
    )
    
    args = parser.parse_args()
    
    # Choose generation method
    if args.legacy:
        print("⚠️  Using legacy single-stage generation\n")
        output_path = generate_experience(
            scenario_id=args.scenario,
            role_ids=args.roles,
            output_file=args.output
        )
    else:
        print("🚀 Using multi-stage generation pipeline\n")
        output_path = generate_experience_multistage(
            scenario_id=args.scenario,
            role_ids=args.roles,
            output_file=args.output
        )
    
    # Run validation if requested
    if args.validate:
        print("\n" + "="*80)
        print("RUNNING VALIDATION")
        print("="*80)
        
        try:
            from validate_scenario import ScenarioValidator, ValidationLevel
            from scenario_editor_agent import ScenarioEditorAgent
            
            max_attempts = 3
            attempt = 0
            editor = ScenarioEditorAgent()
            
            while attempt < max_attempts:
                attempt += 1
                print(f"\n--- Validation Attempt {attempt}/{max_attempts} ---\n")
                
                # Run validation
                validator = ScenarioValidator(Path(output_path))
                report = validator.validate_all()
                
                # Show results
                critical_count = len([i for i in report.issues if i.level == ValidationLevel.CRITICAL])
                important_count = len([i for i in report.issues if i.level == ValidationLevel.IMPORTANT])
                advisory_count = len([i for i in report.issues if i.level == ValidationLevel.ADVISORY])
                
                if report.passed:
                    print(f"\n✅ VALIDATION PASSED!")
                    print(f"   Advisory: {advisory_count}")
                    break
                
                print(f"\n❌ VALIDATION FAILED")
                print(f"   Critical: {critical_count}")
                print(f"   Important: {important_count}")
                
                # Show first few critical issues
                critical_issues = [i for i in report.issues if i.level == ValidationLevel.CRITICAL]
                print(f"\n   Critical Issues:")
                for issue in critical_issues[:5]:
                    print(f"     • [{issue.rule_number}] {issue.title}")
                
                if attempt < max_attempts:
                    print(f"\n🤖 Scenario Editor Agent fixing issues...")
                    
                    # Use Editor Agent to fix issues
                    results = editor.fix_issues(
                        Path(output_path),
                        critical_issues,
                        max_issues=5
                    )
                    
                    success_count = sum(1 for r in results if r.success)
                    print(f"   Fixed {success_count}/{len(results)} issues")
                else:
                    print(f"\n⚠️  Max validation attempts ({max_attempts}) reached.")
                    print(f"   Scenario has remaining issues. Manual review recommended.")
                    
                    # Show full report for manual fixing
                    print("\n" + "="*80)
                    print("FULL VALIDATION REPORT")
                    print("="*80)
                    report.print_report()
                    
                    sys.exit(1)
            
        except Exception as e:
            print(f"\n❌ Validation error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
