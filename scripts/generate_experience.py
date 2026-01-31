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


def build_prompt(scenario, roles, design_guide, npc_guide, example):
    """Build the prompt for Gemini to generate dependency tree."""
    
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
    
    prompt = f"""You are an expert game designer creating a dependency tree for a collaborative heist game.

## Your Task

Generate a complete dependency tree markdown file for this heist scenario.

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

## Example Dependency Tree

Here's an example of the format and quality expected:

{example}

## Requirements

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
- Objective
- Scenario overview
- Locations list (organized by category)
- Task types legend
- Roles & Dependencies (detailed task list for each role)
- Task summary with statistics
- Dependency tree diagrams (full + simplified)
- Key collaboration points
- NPC personality highlights

**Important**: 
- Every task must have a *Location:* field
- Every NPC must have a personality trait and sample dialogue
- Search tasks must specify what's found
- Follow dependencies logically (can't crack safe before reaching it)
- Make it fun and replayable with quirky NPCs!

Now generate the complete dependency tree for the scenario above.
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
                'max_output_tokens': 8192,  # Long output needed
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
