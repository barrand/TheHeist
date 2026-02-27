"""
Stage 1: Story Generator

Generates a semi-structured heist story in plain English using a template format.
This separates creative storytelling from strict validation rules.

The output is designed to be:
1. Natural for LLMs to generate
2. Easy for humans to read
3. Parseable by structure_extractor.py
"""

import json
from pathlib import Path
from typing import List, Dict
from google import genai


def load_json(file_path: Path) -> dict:
    """Load JSON data from file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def load_text(file_path: Path) -> str:
    """Load text content from file"""
    with open(file_path, 'r') as f:
        return f.read()


def build_story_prompt(scenario: dict, roles: List[dict]) -> str:
    """Build prompt for narrative story generation"""
    
    role_names = [role['name'] for role in roles]
    role_list = ', '.join(role_names)
    
    # Build role minigames reference
    role_minigames_sections = []
    for role in roles:
        minigames = role.get('minigames', [])
        if minigames:
            mg_list = ', '.join([f"{mg['id']}" for mg in minigames])
            role_minigames_sections.append(f"**{role['name']}**: {mg_list}")
        else:
            role_minigames_sections.append(f"**{role['name']}**: coordination only")
    
    minigames_text = '\n'.join(role_minigames_sections)
    
    prompt = f"""You are a heist game designer. Generate a heist story using a semi-structured format that's easy to parse.

## Scenario Brief

**Scenario**: {scenario['name']}
**Objective**: {scenario['objective']}
**Summary**: {scenario['summary']}
**Roles**: {role_list} ({len(roles)} players)

## Available Minigames by Role

{minigames_text}

## Output Format

Generate a heist story using this exact template format:

```
STORY_START

OBJECTIVE: [Main objective in one sentence]

LOCATIONS:
- LOCATION: Safe House [safe_house]
  DESC: The crew's planning headquarters
- LOCATION: Bank Lobby [bank_lobby]
  DESC: Public entrance with security desk
- LOCATION: Vault Room [vault_room]
  DESC: High-security room with the target

[Continue with 6-9 locations for {len(roles)} players]

ITEMS:
- ITEM: Security Badge [security_badge]
  AT: safe_house
  HIDDEN: false
  DESC: Employee ID badge
  NEEDED_FOR: Accessing secure areas
  UNLOCK: None
- ITEM: Vault Key [vault_key]
  AT: bank_lobby
  HIDDEN: true
  DESC: Master key for vault
  NEEDED_FOR: Opening the vault
  UNLOCK: AFTER Task H2 (guard must be distracted first)

[Continue with items needed for the heist]

NPCS:
- NPC: Security Guard Mike [security_guard_mike]
  AT: bank_lobby
  ROLE: Security Guard
  PERSONALITY: Bored veteran who loves talking about sports
  PROVIDES: guard_distracted (will leave post if given a reason)
  STORY_CONTEXT: Mike is the only guard in the lobby. He's been working double shifts. He won't leave unless someone gives him a very good reason.
- NPC: Bank Manager Elena [bank_manager_elena]
  AT: vault_room
  ROLE: Bank Manager
  PERSONALITY: Strict, rule-following, suspicious of strangers
  PROVIDES: vault_code (knows the vault combination)
  STORY_CONTEXT: Elena has the vault code memorized. She only opens it during business hours with proper authorization.

[Continue with 6-10 NPCs that provide unique information or actions]

TASKS:

STARTING_TASKS: (Tasks that can begin immediately)
- Task H1 (hacker) at safe_house: Search for equipment
  TYPE: search
  FIND: security_badge, lockpicks
  UNLOCK: H2

- Task MM1 (mastermind) at safe_house: Plan the approach
  TYPE: info_share
  SHARE: heist_plan_briefing with ALL
  UNLOCK: MM2, D1

[List 3-5 starting tasks with Prerequisites: None]

TASK_CHAIN:
- Task H2 (hacker) at bank_lobby: Talk to security guard
  TYPE: npc_llm
  TALK_TO: security_guard_mike
  GET: guard_distracted
  NEEDS: security_badge (from H1)
  UNLOCK: H3, SC1

- Task H3 (hacker) at vault_room: Disable vault alarm
  TYPE: minigame (wire_connecting)
  NEEDS: guard_distracted (from H2)
  UNLOCK: SC2

- Task SC1 (safe_cracker) at bank_lobby: Pick lobby door lock
  TYPE: minigame (lock_picking)
  NEEDS: lockpicks (from H1), guard_distracted (from H2)
  UNLOCK: SC2

- Task SC2 (safe_cracker) at vault_room: Crack vault safe
  TYPE: minigame (dial_rotation)
  NEEDS: SC1 (door must be open), H3 (alarm disabled)
  FINAL: true (heist completes when this finishes)

[Continue with all tasks in dependency order]

STORY_END
```

## Critical Requirements

### Location Count
- **{len(roles)} players**: Generate 6-9 locations
- Include: safe house, entry points, public areas, restricted areas, target location, getaway spot

### Task Count & Balance
- **Total**: 30-40 tasks for {len(roles)} players
- **Per role**: 3-8 tasks each (distribute evenly)
- **Task types**:
  - 60-70% social: npc_llm, search, handoff, info_share
  - 30-40% minigames
- **Include**:
  - 3+ HANDOFF tasks (item transfers between players)
  - 2+ INFO_SHARE tasks (verbal coordination)
  - 6-10 SEARCH tasks (finding items)

### NPC Rules
- Create 6-10 NPCs
- Each NPC provides EXACTLY ONE outcome (info or action)
- NPCs are AI characters (guards, staff, civilians) - NOT player roles
- Give each NPC personality and context

### Item Rules
- If HIDDEN: true, item MUST have UNLOCK condition
- Items without UNLOCK are immediately available when searched
- Use UNLOCK to gate items behind task completion

### Task Dependencies
- Start with 3-5 STARTING_TASKS (no prerequisites)
- Chain tasks logically (can't crack vault before disabling alarm)
- Every role should have at least 1 starting task
- Use NEEDS to list prerequisites (tasks, outcomes, items)
- Mark final objective tasks with FINAL: true

### ID Format
- Use snake_case for all IDs
- Location IDs: safe_house, bank_lobby, vault_room
- NPC IDs: security_guard_mike, bank_manager_elena
- Item IDs: security_badge, vault_key
- Outcome IDs: guard_distracted, vault_code
- Task IDs: H1, H2, SC1, SC2, MM1, etc. (ROLE_PREFIX + NUMBER)

### Role Prefixes
- Mastermind: MM
- Hacker: H
- Safe Cracker: SC
- Driver: D
- Insider: I
- Grifter: G
- Muscle: M
- Lookout: L
- Fence: F
- Cat Burglar: CB
- Cleaner: CL
- Pickpocket: PP

## Creativity Guidelines

BE CREATIVE! Think about the scenario:
- Museum heist? Think art, security, gala events, curators
- Train robbery? Think schedules, conductors, passengers, cargo
- Bank job? Think vaults, managers, protocols, customers

Make each NPC memorable with distinct personalities, wants, and problems.
Create organic task chains that feel natural to the story.
Allow multiple valid approaches when it makes sense.

## Example Story Structure

For a 3-player museum heist with Mastermind, Hacker, Safe Cracker:

```
STORY_START

OBJECTIVE: Steal the Crown Jewels from the museum vault during the gala event

LOCATIONS:
- LOCATION: Safe House [safe_house]
  DESC: Abandoned warehouse used for planning
- LOCATION: Museum Entrance [museum_entrance]
  DESC: Grand marble entrance with security checkpoint
... (4 more locations)

ITEMS:
- ITEM: Security Badge [security_badge]
  AT: safe_house
  HIDDEN: false
  DESC: Fake museum security ID
  NEEDED_FOR: Bypassing checkpoints
  UNLOCK: None

NPCS:
- NPC: Guard Thompson [guard_thompson]
  AT: museum_entrance
  ROLE: Security Guard
  PERSONALITY: Sports fan who gets easily distracted
  PROVIDES: entrance_access (will leave post to check a "disturbance")
  STORY_CONTEXT: Only guard at entrance, loves basketball

TASKS:

STARTING_TASKS:
- Task MM1 (mastermind) at safe_house: Search for equipment
  TYPE: search
  FIND: security_badge, gala_invitation
  UNLOCK: MM2, H1

TASK_CHAIN:
- Task H1 (hacker) at safe_house: Brief Safe Cracker on plan
  TYPE: info_share
  SHARE: vault_approach_plan with safe_cracker
  NEEDS: MM1 (planning done)
  UNLOCK: SC1

- Task MM2 (mastermind) at museum_entrance: Distract security guard
  TYPE: npc_llm
  TALK_TO: guard_thompson
  GET: entrance_access
  NEEDS: security_badge (from MM1)
  UNLOCK: MM3, SC1
... (continue chain)

STORY_END
```

Now generate a complete heist story for the scenario above using this exact format.
"""
    
    return prompt


def generate_story(
    scenario_id: str,
    role_ids: List[str],
    api_key: str,
    model: str = "gemini-2.5-flash",
    data_dir: Path = None
) -> str:
    """
    Generate a semi-structured heist story
    
    Args:
        scenario_id: Scenario ID (e.g., "museum_gala_vault")
        role_ids: List of role IDs (e.g., ["mastermind", "hacker"])
        api_key: Gemini API key
        model: Gemini model to use
        data_dir: Path to shared_data directory
    
    Returns:
        Semi-structured story text
    """
    # Load scenario and role data
    if data_dir is None:
        data_dir = Path(__file__).parent.parent.parent.parent / 'shared_data'
    
    scenarios = load_json(data_dir / 'scenarios.json')
    roles_data = load_json(data_dir / 'roles.json')
    
    # Get scenario details
    scenario = None
    for s in scenarios['scenarios']:
        if s['scenario_id'] == scenario_id:
            scenario = s
            break
    
    if not scenario:
        raise ValueError(f"Scenario '{scenario_id}' not found")
    
    # Get role details
    roles = []
    for role in roles_data['roles']:
        if role['role_id'] in role_ids:
            roles.append(role)
    
    if len(roles) != len(role_ids):
        raise ValueError(f"Some roles not found: {role_ids}")
    
    # Build prompt
    prompt = build_story_prompt(scenario, roles)
    
    # Call Gemini API
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0.8,  # Higher temp for creativity
            top_p=0.95,
            top_k=40,
            max_output_tokens=16000,
        )
    )
    
    if not response.text:
        raise RuntimeError("No response from Gemini API")
    
    return response.text


if __name__ == '__main__':
    import argparse
    import sys
    
    # Add parent directories to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import GEMINI_API_KEY, GEMINI_EXPERIENCE_MODEL, DATA_DIR
    
    parser = argparse.ArgumentParser(description="Generate heist story (Stage 1)")
    parser.add_argument("--scenario", required=True, help="Scenario ID")
    parser.add_argument("--roles", nargs="+", required=True, help="Role IDs")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    print(f"🎬 Generating heist story...")
    print(f"   Scenario: {args.scenario}")
    print(f"   Roles: {', '.join(args.roles)}")
    print()
    
    story = generate_story(
        scenario_id=args.scenario,
        role_ids=args.roles,
        api_key=GEMINI_API_KEY,
        model=GEMINI_EXPERIENCE_MODEL,
        data_dir=DATA_DIR
    )
    
    # Save to file
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path('output/stories') / f"{args.scenario}_{'_'.join(args.roles[:2])}_story.txt"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(story)
    
    print(f"✅ Story generated ({len(story.split())} words)")
    print(f"💾 Saved to: {output_path}")
