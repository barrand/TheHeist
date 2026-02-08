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


def build_prompt(scenario, roles, design_guide, npc_guide, discovery_guide, example):
    """Build the prompt for Gemini to generate dependency tree with discovery system."""
    
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
    
    prompt = f"""You are an expert game designer creating an experience file for a discovery-based collaborative heist game.

## Your Task

Generate a complete experience file with a **discovery-based task system** for this heist scenario.

**Scenario**: {scenario['name']} (ID: {scenario['scenario_id']})
**Objective**: {scenario['objective']}
**Summary**: {scenario['summary']}
**Selected Roles**: {role_list}
**Player Count**: {len(roles)} players

## Available Minigames by Role

{minigames_section}

## Discovery System Guide

{discovery_guide}

## Design Guidelines

{design_guide}

## NPC Personality Guidelines

{npc_guide}

## Example Experience File

Here's an example of the format and quality expected:

{example}

## CRITICAL: Discovery System Requirements

### 1. Team Objectives (1-3 high-level goals)
Start with clear objectives visible to ALL players:
- ✅ Example: "🔓 Get Into the Safe"
- ✅ Example: "💎 Steal the Diamond" 
- ✅ Example: "🚪 Escape the Building"
- Keep them action-oriented and clear

### 2. Discovery Tasks (Create 4-8 unique discovery moments)
Tasks that REVEAL information and SPAWN new tasks or options:
- 🔍 **Examine** tasks (inspect objects, locations, systems)
- 🔍 **Search** tasks (find items, clues, hidden things)
- 💬 **Investigate** tasks (talk to NPCs, observe behavior, eavesdrop)
- 🤝 **Coordinate** tasks (combine what multiple players learned)

**Discovery tasks should include:**
- `[DISCOVERY]` tag in the task description
- `Spawns:` field listing what tasks/options appear after completion
- `Discovery:` field describing what players learn
- Be creative! Not all discoveries are codes - they can reveal locations, people, timing, methods, weaknesses

### 3. Organic Discovery Design (MOST IMPORTANT!)
Create diverse, creative discovery moments that feel natural to the scenario:

**PRINCIPLES:**
1. **Variety is key** - Don't repeat patterns. Each discovery should feel unique
2. **Context matters** - Discoveries should fit the location and scenario
3. **Natural revelation** - Information emerges through exploration, not handed over
4. **Multiple steps** - Chain 2-4 small discoveries together
5. **Player agency** - Give choices that lead to different information

**DIVERSE DISCOVERY TYPES:**

**A) Object Examination**
- Examine painting → Notice it's slightly crooked → Behind it is a hidden panel
- Inspect vehicle → Find tracking device → Must disable or leave it
- Check security system → See unusual wiring → Someone modified it recently

**B) NPC Information Exchange**
- NPC needs favor → You help → They share what they know
- NPC has problem → You solve it → They become ally and provide access
- NPC is chatty → Let them ramble → Accidentally reveals useful detail
- NPC is suspicious → Build trust over multiple conversations → Finally opens up

**C) Environmental Storytelling**
- Search desk → Find multiple items that together reveal a pattern
- Notice schedule → Cross-reference with another clue → Discover timing window
- Observe NPC behavior → They keep checking their watch → Follow them at that time
- Find torn note → Another player finds other half → Combine to read full message

**D) Team Coordination Discoveries**
- Player A overhears conversation → Player B finds related document → Together they understand
- Player A gets partial code → Player B gets other half → Must communicate to assemble
- Player A distracts NPC → Player B can then access their office
- Player A creates opportunity → Player B must be ready to exploit it

**E) Unexpected Consequences**
- Search too loudly → Guard becomes suspicious → New challenge appears
- Take item without permission → NPC notices later → Must make amends
- Complete task too quickly → Raises alarm → Team must adapt plan

**VARIETY IN MECHANISMS:**
- **NOT JUST CODES**: Discoveries can reveal locations, people, timing, methods, weaknesses
- **NOT JUST NPCs**: Examine objects, search rooms, observe patterns, connect clues
- **NOT JUST LINEAR**: Create branching paths where different discoveries lead to different solutions

### 4. Multiple Discovery Paths (When Appropriate)
Sometimes offer 2-3 ways to discover information or solve problems:
- Create paths that suit different roles (technical vs social vs physical)
- Each path should feel valid and interesting (not one "correct" path)
- Paths can converge later or lead to same goal through different means
- Don't force branching everywhere - linear is fine for some tasks

### 5. Team vs Player-Specific Tasks

**Team Tasks (👥)** - Multiple players can see and complete:
- "Find Vault Combination" (anyone can search for it)
- "Distract Guard" (anyone can attempt)
- Mark these with `[TEAM TASK]` in description

**Player-Specific Tasks** - Only one role can do:
- "Crack Safe" (Safe Cracker only)
- "Hack Terminal" (Hacker only)
- Specify `Role: Safe Cracker` in task

### 6. Task Spawning Chains
Show clear progression where discoveries lead to new options:
```
Initial: 🔍 Eavesdrop on Guards [DISCOVERY]
  Spawns → Team: Check Roof Access [TEAM TASK]
  
After checking: 🔍 Check Roof Access [DISCOVERY]  
  Discovery: "Door unlocked but camera watches it"
  Spawns → Hacker: Disable Camera
  Spawns → Team: Create Distraction [TEAM TASK]
  
After both complete: New Location Unlocked: Roof
  New tasks available at Roof location
```
Mix linear chains (A→B→C) with parallel options (A→B OR A→C) for variety

### 7. Make Discoveries Feel Organic

**Discoveries should emerge naturally from:**
- Exploring the environment (searching, examining, noticing details)
- Interacting with NPCs (conversations, observations, building relationships)  
- Coordinating with team (combining information, timing actions)
- Attempting tasks (failures reveal new information too!)
- Following logical chains (A leads to B leads to C)

**Vary what discoveries reveal:**
- Locations (hidden passages, alternative routes)
- People (who knows what, who has access, who can help)
- Timing (when guards change, when deliveries arrive)
- Methods (how to bypass security, how to distract NPCs)
- Items (what tools are needed, where to find them)
- Weaknesses (security gaps, NPC vulnerabilities)
- Backstory (motivations, relationships, history)

**Make NPCs feel real, not just info dispensers:**
- Give them wants, needs, problems, quirks
- Let conversations flow naturally, not just Q&A
- Have them reveal info through personality, not exposition dumps
- Make players work to get information (build trust, solve problems, trade favors)
- Add red herrings and misdirection (NPCs don't know they're giving clues!)

## NPC Conversation System Format (CRITICAL!)

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
- **Information Known**:
  - `info_id` HIGH: The ONE piece of info this NPC provides (tagged with ID)
  - LOW: Flavor text they might share (no ID = not tracked, just conversation filler)
  - LOW: More flavor to make the NPC feel real
- **Actions Available**:
  - (none, if this NPC provides info instead of an action)
  - OR: `action_id` HIGH: The ONE action this NPC can perform (if action-type NPC)
- **Cover Story Options**:
  - `cover_id`: "What the player claims to be" -- Trust: HIGH (why NPC trusts this cover)
  - `another_cover`: "Another cover story" -- Trust: LOW (why NPC distrusts this cover)
  - `third_cover`: "Third option" -- Trust: MEDIUM (explanation)
```

Rules for NPCs:
- ONE outcome per NPC: each NPC has exactly ONE tagged info item OR ONE action (not both, not multiple). This is their sole purpose in the story.
- Additional LOW items (no ID) can be added as flavor to make conversation natural, but only ONE item has an ID.
- Each NPC needs exactly 3 cover story options (one HIGH, one MEDIUM, one LOW trust)
- Info/Action IDs must be snake_case and unique across the experience
- Every NPC must be targeted by exactly one task with a matching Target Outcome
- If you need more outcomes, add more NPCs -- don't overload one NPC

### Task Prerequisite Format:
```markdown
1. **MM1. 💬 NPC_LLM** - Task Description
   - *Description:* Detailed description
   - *NPC:* `npc_id` (NPC Name)
   - *Target Outcomes:* `single_outcome_id`
   - *Location:* Location Name
   - *Prerequisites:* None (starting task)

2. **MM2. 🎮 minigame_id** - Task Description
   - *Description:* Detailed description
   - *Location:* Location Name
   - *Prerequisites:*
     - Task `MM1` (description of why)
     - Outcome `info_id` (what info is needed)
     - Item `item_id` (what item is needed)
```

Rules for Tasks:
- Use typed prerequisites: `Task`, `Outcome`, `Item` (not plain dependency IDs)
- NPC tasks MUST have `*Target Outcomes:*` with exactly ONE outcome ID (matches the NPC's single tagged item/action)
- `*NPC:*` field must reference NPC by backtick ID: `*NPC:* \`npc_id\` (Name)`
- Search tasks use `*Search Items:*` instead of `*Find:*`
- Any player role can do search/social tasks; role-locked tasks are minigames requiring specific skills

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
11. **Include cover story options** for every NPC (3 per NPC, varying trust)
12. **Tag all NPC info** with snake_case IDs for outcome tracking

## CREATIVITY GUIDELINES ⭐

**BE CREATIVE! Don't copy the examples directly:**
- Create unique discovery moments that fit YOUR scenario
- Vary the types of discoveries (not all codes/combinations!)
- Make each NPC distinct with different problems and personalities
- Think about what would be fun and surprising for players
- Create organic chains where discoveries feel natural
- Allow multiple valid approaches when it makes sense
- Not every task needs to be a discovery - straightforward tasks are good too!

**Think about the scenario:**
- Museum heist? Think about art, security systems, gala events, curators, collectors
- Train robbery? Think about schedules, conductors, passengers, cargo, stations
- Bank job? Think about vaults, managers, security protocols, customers, routines

**Make each experience feel fresh and replayable!**

## Output Format

Generate a complete markdown file with:
- Generation header with scenario/role info
- **TEAM OBJECTIVES section (NEW!)** - List 1-3 high-level goals
- Scenario overview
- Locations list (organized by category)
- Task types legend
- **Discovery Tasks section (NEW!)** - List discovery moments
- Roles & Dependencies (detailed task list for each role)
  - Mark discovery tasks with [DISCOVERY] and Spawns: field
  - Mark team tasks with [TEAM TASK]
  - Show task visibility (team vs role-specific)
- Task summary with statistics
- Dependency tree diagrams (full + simplified)
- Key collaboration points
- NPC personality highlights with **clue design notes**

**Important**: 
- Every task must have a *Location:* field
- Every NPC must have a personality trait and sample dialogue
- **NPCs with clues must show how clues are woven into conversation**
- Search tasks must specify what's found
- Discovery tasks must specify what they spawn
- Follow dependencies logically (can't crack safe before examining it)
- Make clues subtle but discoverable (players should feel clever!)
- Create multiple paths to same discovery
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

## CONCRETE EXAMPLES: Diverse Discovery Patterns

Show variety! Here are different discovery patterns to inspire you (don't copy exactly, create your own):

### EXAMPLE 1: Environmental Discovery Chain
```markdown
1. 🔍 **Search Loading Dock** [DISCOVERY] [TEAM TASK]
   - *Location:* Loading Dock
   - *Description:* Check for entry points and useful equipment
   - *Discovery:* "Loading schedule on clipboard. Next delivery: 8:30 PM tonight. Driver: Carlos"
   - *Spawns:* "Wait for Delivery" (team), "Talk to Carlos" (team)

2. 💬 **Intercept Delivery Driver** [TEAM TASK] [DISCOVERY]
   - *Location:* Loading Dock
   - *Description:* Meet Carlos when he arrives at 8:30 PM
   - *Timing:* Only available after 8:30 PM game time
   - *NPC:* Carlos (overworked, chatty, hates his boss)
   - *Discovery:* "Carlos complains his boss makes him use the side entrance because the main loading bay is 'being fumigated' - suspicious!"
   - *Spawns:* "Investigate Main Loading Bay" (team)

3. 🔍 **Investigate Suspicious Area** [DISCOVERY]
   - *Location:* Main Loading Bay
   - *Description:* Check why this area is supposedly "fumigated"
   - *Discovery:* "No fumigation. But there IS a hidden security door you wouldn't have found otherwise!"
   - *Spawns:* "Find Way Through Security Door" (Hacker)
```

### EXAMPLE 2: Split Team Discovery
```markdown
1. 💬 **Eavesdrop on Guards** [DISCOVERY]
   - *Location:* Hallway
   - *Role:* Insider (has legitimate reason to be nearby)
   - *Description:* Stand near guards and listen to their conversation
   - *Discovery:* "Guard mentions: 'Did you lock the roof access after the maintenance crew left?'"
   - *Spawns:* "Check Roof Access" (team)

2. 🔍 **Check Roof Access** [TEAM TASK] [DISCOVERY]
   - *Location:* Stairwell
   - *Description:* Try the roof access door
   - *Discovery:* "Door is unlocked! But there's a camera pointing at it."
   - *Spawns:* "Disable Camera" (Hacker), "Create Distraction" (team)

3. 🤝 **Coordinate Roof Entry** [TEAM COORDINATION]
   - *Description:* Hacker disables camera, team uses roof access simultaneously
   - *Dependencies:* Both "Disable Camera" AND "Create Distraction" complete
   - *Spawns:* New location unlocked: Roof
```

### EXAMPLE 3: Item Assembly Discovery
```markdown
1. 🔍 **Search Janitor's Closet** [DISCOVERY]
   - *Location:* Janitor's Closet
   - *Discovery:* "Find a master key ring, but it's missing the key for the exhibit hall"
   - *Spawns:* "Find Missing Key" (team)

2. 💬 **Ask Janitor About Key** [TEAM TASK]
   - *Location:* Break Room
   - *NPC:* Janitor (grumpy, territorial)
   - *Discovery:* "Janitor says security confiscated the exhibit key last week after 'an incident'"
   - *Spawns:* "Get Key from Security" (team)

3. 🔍 **Search Security Office** [DISCOVERY]
   - *Location:* Security Office  
   - *Dependencies:* Distract or bypass security guard
   - *Discovery:* "Key is in evidence locker. Locker requires signature from 'Assistant Director'"
   - *Spawns:* "Forge Signature" (team) OR "Get Real Signature" (Insider)
```

### EXAMPLE 4: Observation-Based Discovery
```markdown
1. 🔍 **Observe Gallery Patterns** [DISCOVERY]
   - *Location:* Gallery
   - *Description:* Watch guard patrol routes for 10 minutes
   - *Discovery:* "Guard checks this room every 15 minutes. Takes 3 minutes to complete circuit. But every hour on the hour, two guards check together."
   - *Spawns:* "Plan Heist Timing" (Mastermind)

2. 📋 **Calculate Time Window** [TEAM COORDINATION]
   - *Description:* Use patrol information to determine safe windows
   - *Dependencies:* "Observe Gallery Patterns" complete
   - *Discovery:* "Best window: 12 minutes after each hour. Team has 10 minute window before next patrol."
   - *Spawns:* Timed challenges become available
```

### EXAMPLE 5: Branching Discovery (Multiple Solutions)
```markdown
### TEAM OBJECTIVE: Get Access to Server Room

**Path A: Social Engineering**
1. 💬 Talk to IT Admin → Learn they love retro video games
2. 🔍 Find Rare Game Cartridge → Search office
3. 🤝 Trade Game for Access → IT Admin gives temporary badge

**Path B: Technical**  
1. 🎮 Hack Badge System → Clone existing badge
2. 🔍 Steal Someone's Badge → Pickpocket during event
3. 🤝 Return Badge → Give back before noticed (optional, affects difficulty)

**Path C: Physical**
1. 🔍 Find Air Duct → Search blueprints
2. 🎮 Navigate Ducts → Cat Burglar minigame
3. 💪 Remove Vent Cover → Muscle helps from inside

All three paths lead to same objective but require different roles and create different stories!
```

**FORMATTING RULES:**
- Use `[DISCOVERY]` for tasks that reveal new information or spawn tasks
- Use `[TEAM TASK]` for tasks any role can attempt
- Use `[TEAM COORDINATION]` for tasks requiring multiple players
- Include *Spawns:* field listing what tasks/options appear after completion
- Include *Discovery:* field describing what players learn
- Show *Dependencies:* for tasks that require previous completion
- Add *Multiple Paths:* when there are different ways to achieve same goal
- Make NPCs unique with distinct personalities (not just information vendors!)

**IMPORTANT REMINDERS:**
- Be creative! Don't copy these examples directly
- Vary the discovery types throughout the experience
- Not every task needs to be a discovery - mix in straightforward tasks too
- Create organic chains where discoveries lead naturally to next steps
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
    discovery_guide = load_text(DESIGN_DIR / 'discovery_system_design.md')
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
    print(f"✓ Loaded discovery system guide")
    print()
    
    # Build prompt
    print("🤖 Building prompt with discovery system...")
    prompt = build_prompt(scenario, selected_roles, design_guide, npc_guide, discovery_guide, example)
    
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


def main():
    parser = argparse.ArgumentParser(
        description='Generate a complete heist experience for a scenario',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_experience.py --scenario museum_gala_vault --roles mastermind hacker safe_cracker
  python generate_experience.py --scenario train_robbery_car --roles mastermind muscle cat_burglar driver
  python generate_experience.py --scenario museum_gala_vault --roles mastermind fence hacker insider --output backend/experiences/my_heist.md
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
    
    args = parser.parse_args()
    
    # Generate the heist experience
    generate_experience(
        scenario_id=args.scenario,
        role_ids=args.roles,
        output_file=args.output
    )


if __name__ == '__main__':
    main()
