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

## Design Guidelines

{design_guide}

## NPC Personality Guidelines

{npc_guide}

## Example Experience File

Here's an example of the format and quality expected:

{example}

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
- 💬 **NPC_LLM**: Dialogue or interaction with AI-controlled character
- 🔍 **Search**: Player searches a location for items
- 🤝 **Handoff**: Physical item transfer between players (tracked in inventory)
- 🗣️ **Info Share**: Verbal information exchange between players (real-life conversation)

**No other task types are allowed.** Every task a player sees must have a clear way to complete it:
- Minigame → play the minigame
- NPC_LLM → talk to the NPC and achieve the outcome
- Search → go to the location and search for items
- Handoff → transfer an item to another player
- Info Share → tell another player the information, then confirm shared

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
