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
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, DATA_DIR, DESIGN_DIR, EXAMPLES_DIR

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


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

### 2. Discovery Tasks (Create 4-8 discovery moments)
Tasks that REVEAL information and SPAWN new tasks:
- 🔍 **Examine** tasks (inspect objects/locations)
  - Example: "Examine the Safe" → reveals it needs 6-digit code
- 🔍 **Search** tasks (find items/clues in rooms)
  - Example: "Search Office" → finds personnel file with clues
- 💬 **Investigate** tasks (ask NPCs questions)
  - Example: "Talk to Janitor" → reveals secret about guard schedule

**Discovery tasks MUST include:**
- `[DISCOVERY]` tag in the task description
- `Spawns:` field listing what tasks appear after completion
- Clear description of what's discovered

### 3. NPC Clue Design (MOST IMPORTANT!)
Create NPCs who reveal clues through **natural conversation**:

**✅ GOOD - Subtle & Natural:**
```
Harold Matthews (vault manager, proud dad):
"My three kids are my world! Emma just turned 13, Lucas is 12, 
and Olivia is 10. I always say those three numbers - 13, 12, 10 - 
are all I really think about!"
```
→ Players must DEDUCE that 131210 might be the combination

**❌ BAD - Too Obvious:**
```
Guard: "The safe combination is 131210."
```
→ No discovery, no fun!

**Design Pattern for NPC Clues:**
1. Give NPC a personality trait (proud parent, workaholic, collector, etc.)
2. Have them talk about their passion naturally
3. Weave clues into the conversation (ages, dates, addresses, names)
4. Make it require 2-3 conversational choices to get the full clue
5. Add misdirection (mention other numbers/facts that aren't relevant)

**Example Clue Patterns:**
- **Ages/Dates**: Parent mentions kids' ages → combination code
- **Addresses**: NPC mentions childhood home → locker number
- **Names**: Spouse's name → password
- **Collections**: Collector mentions rare item → auction catalog number
- **Habits**: Always drinks coffee at 3:30pm → keypad code 1530

### 4. Multiple Discovery Paths
Create 2-3 ways to discover the same information:
- **Path A (Direct)**: Hacker searches personnel files → finds ages
- **Path B (Social)**: Grifter talks to NPC → hears about kids
- **Path C (Observation)**: Anyone searches office → finds family photo with ages written on back

### 5. Team vs Player-Specific Tasks

**Team Tasks (👥)** - Multiple players can see and complete:
- "Find Vault Combination" (anyone can search for it)
- "Distract Guard" (anyone can attempt)
- Mark these with `[TEAM TASK]` in description

**Player-Specific Tasks** - Only one role can do:
- "Crack Safe" (Safe Cracker only)
- "Hack Terminal" (Hacker only)
- Specify `Role: Safe Cracker` in task

### 6. Task Spawning Chain
Show clear progression:
```
Initial: 🔍 Examine Safe [DISCOVERY]
  Spawns → Team: Find Combination [TEAM TASK]
  Spawns → Safe Cracker: Crack Safe [Locked: needs combination]
  
After "Find Combination" complete:
  Unlocks → Safe Cracker: Crack Safe [NOW AVAILABLE]
```

### 7. Clue Integration Examples

**PATTERN: The Personal Connection**
```
NPC: Museum Director (art obsessed, detail-oriented)
Clue embedded: "The Renaissance period, 1478 specifically, was pivotal..."
Code revealed: 1478 (security code)
```

**PATTERN: The Routine**
```
NPC: Security Guard (punctual, creature of habit)
Clue embedded: "I've done the same route for 12 years. Check cameras 
at 7:15, 9:30, and 11:45. Like clockwork."
Code revealed: 071593011 (guard's pattern)
```

**PATTERN: The Complaint**
```
NPC: Janitor (overworked, bitter)
Clue embedded: "Been here since 2001. Started with just 4 floors to clean,
now it's all 12 floors. Back in 2001, things were simpler..."
Code revealed: 20010412 (hiring date, initial floors = 2001-04-12)
```

## Standard Requirements

1. **Follow the exact format** shown in the example
2. **Use only minigames** listed above for each role
3. **Include NPC personalities** with traits, speech patterns, and sample dialogue
4. **Add 🔍 Search tasks** for room inventory mechanics (8-12 search tasks)
5. **Create NPC request chains** where NPCs ask for items before helping
6. **Target 60-70% social interactions** (NPC + Search + Handoffs + Info shares)
7. **Create 3-5 critical tasks per role** with clear dependencies
8. **Include location list** at the beginning (12-18 locations)
9. **Add generation header** showing scenario, roles, and player count
10. **Generate both full and simplified Mermaid diagrams**

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

## CONCRETE EXAMPLE: Safe Combination Discovery

Here's exactly how to format a discovery-based task chain:

```markdown
### TEAM OBJECTIVE: 🔓 Get Into the Safe

**Safe Cracker Tasks:**

1. 🔍 **Examine the Safe** [DISCOVERY]
   - *Location:* Vault Room
   - *Description:* Inspect the safe to determine what's needed to open it
   - *Dependencies:* Access to Vault Room
   - *Spawns:* "Find Vault Combination" (team), "Crack Safe" (Safe Cracker, locked)
   - *Discovery:* "Vanderbilt Model 3200. Requires 6-digit combination. Engraved: Property of H. Matthews"

2. 🎮 **Crack Safe** (safe_crack_rotation)
   - *Location:* Vault Room
   - *Description:* Use the combination to open the safe
   - *Dependencies:* "Find Vault Combination" complete
   - *Unlocks After:* Team finds combination

**Team Tasks (anyone can do):**

3. 💬 **Find Who H. Matthews Is** [TEAM TASK] [DISCOVERY]
   - *Location:* Multiple (Curator's Office, Security Room, Grand Hall)
   - *Description:* Discover the identity of the safe's owner
   - *Dependencies:* "Examine the Safe" complete
   - *Spawns:* "Talk to Harold Matthews" (team)
   - *Multiple Paths:*
     - Path A: Ask Curator → reveals he's vault manager
     - Path B: Search Security Files → finds employee record
     - Path C: Ask Gala Guests → hear gossip about him

4. 🔍 **Search Personnel Files** [DISCOVERY]
   - *Location:* Security Room
   - *Description:* Search security office for employee records
   - *Dependencies:* Access to Security Room
   - *Discovery:* "Harold Matthews, Vault Manager. Dependents: Emma (13), Lucas (12), Olivia (10)"
   - *Spawns:* "Talk to Harold Matthews" (team)

5. 💬 **Talk to Harold Matthews** [TEAM TASK] [CLUE]
   - *Location:* Staff Break Room
   - *Description:* Have a conversation with the vault manager
   - *Dependencies:* "Find Who H. Matthews Is" complete
   - *NPC:* Harold Matthews (proud dad, kind, distracted)
   - *Personality:* Only talks about his three kids, very predictable
   - *Clue Design:* 
     - If asked about family: "I have three wonderful children. Emma just turned 13, Lucas is 12, and Olivia is 10."
     - Key line: "I always say those three numbers - 13, 12, 10 - are all I really think about!"
     - Players must deduce: 131210 might be the combination
   - *Spawns:* "Try Combination 131210" (Safe Cracker)

**NPC: Harold Matthews**
- Trait: Proud parent, talks constantly about kids
- Speech Pattern: Warm, enthusiastic about family, mentions ages often
- Sample Dialogue:
  - "My kids are my world! Emma's 13 now, so responsible."
  - "Lucas turned 12 last month - he's growing so fast!"
  - "And my baby Olivia is 10. Those three numbers, that's my life!"
- Clue Integration: Ages (13, 12, 10) = Safe combination (131210)
- Misdirection: Also mentions other numbers (15 years employed, 3 bedroom house) to add challenge
```

**Key Elements:**
- `[DISCOVERY]` tag for tasks that reveal info
- `[TEAM TASK]` for tasks anyone can do
- `[CLUE]` for NPCs who provide puzzle clues
- *Spawns:* field showing what unlocks
- *Dependencies:* showing what's needed first
- *Multiple Paths:* showing different ways to discover same info
- *Clue Design:* section explaining how NPC weaves clue into conversation
- NPC personality with specific dialogue showing how clue emerges naturally

Now generate the complete experience file for the scenario above, following this discovery-based format.
"""
    
    return prompt


def generate_experience(scenario_id, role_ids, output_file=None):
    """Generate complete heist experience using Gemini AI."""
    
    print(f"🎮 Generating heist experience...")
    print(f"   Scenario: {scenario_id}")
    print(f"   Roles: {', '.join(role_ids)}")
    print(f"   Model: {GEMINI_MODEL}")
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
    print(f"🚀 Calling Gemini API ({GEMINI_MODEL})...")
    print("   This may take 30-60 seconds...")
    print()
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,  # Some creativity, but not too much
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 32000,  # Long output needed for full dependency trees
            }
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
            # Default: output/{scenario_id}_{roles}.md
            roles_str = '_'.join(role_ids[:3])  # First 3 roles
            if len(role_ids) > 3:
                roles_str += f'_plus{len(role_ids)-3}'
            output_path = Path('output') / f"{scenario_id}_{roles_str}.md"
        
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
  python generate_experience.py --scenario museum_gala_vault --roles mastermind fence hacker insider --output my_heist.md
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
        help='Output file path (default: output/{scenario}_{roles}.md)'
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
