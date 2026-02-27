"""
Stage 4: Markdown Renderer

Converts validated JSON scenario graph into final markdown format.
Uses templates to ensure consistent formatting and proper ID usage.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

# Import graph structures
sys.path.insert(0, str(Path(__file__).parent))
from structure_extractor import ScenarioGraph, Task, Location, Item, NPC


def render_header(graph: ScenarioGraph) -> str:
    """Render scenario header"""
    role_names = ', '.join([r.replace('_', ' ').title() for r in graph.roles])
    
    return f"""---
---
---
---
---
---
# {graph.objective}

**ID**: `{graph.scenario_id}`
**Scenario**: {graph.objective}
**Selected Roles**: {role_names}
**Player Count**: {graph.player_count} players

## Objective
{graph.objective}

"""


def render_locations(graph: ScenarioGraph) -> str:
    """Render locations section"""
    output = "## Locations\n\n"
    
    # Group locations by category (optional, for now just list them)
    for location in graph.locations:
        output += f"### {location.name}\n"
        output += f"- **ID**: `{location.id}`\n"
        output += f"  - **Name**: {location.name}\n"
        output += f"  - **Description**: {location.description}\n"
        output += f"  - **Visual**: {location.description}\n\n"
    
    output += f"**Total Locations**: {len(graph.locations)}\n\n"
    return output


def render_items(graph: ScenarioGraph) -> str:
    """Render items by location"""
    output = "## Items by Location\n\n"
    
    # Group items by location
    items_by_loc = defaultdict(list)
    for item in graph.items:
        items_by_loc[item.location].append(item)
    
    # Get location names
    loc_names = {loc.id: loc.name for loc in graph.locations}
    
    for loc_id, items in items_by_loc.items():
        loc_name = loc_names.get(loc_id, loc_id.replace('_', ' ').title())
        output += f"### {loc_name}\n"
        
        for item in items:
            output += f"- **ID**: `{item.id}`\n"
            output += f"  - **Name**: {item.name}\n"
            output += f"  - **Description**: {item.description}\n"
            output += f"  - **Visual**: {item.description}\n"
            output += f"  - **Required For**: {item.needed_for}\n"
            output += f"  - **Hidden**: {str(item.hidden).lower()}\n"
            
            if item.unlock_prerequisites:
                output += f"  - **Unlock**:\n"
                for unlock_task in item.unlock_prerequisites:
                    output += f"    - Task `{unlock_task}`\n"
            
            output += "\n"
    
    return output


def render_npcs(graph: ScenarioGraph) -> str:
    """Render NPCs section"""
    output = "## NPCs\n\n"
    
    for npc in graph.npcs:
        output += f"### {npc.role} - {npc.name}\n"
        output += f"- **ID**: `{npc.id}`\n"
        output += f"- **Role**: {npc.role}\n"
        output += f"- **Location**: `{npc.location}`\n"
        output += f"- **Age**: 30\n"  # Default age
        output += f"- **Gender**: unknown\n"  # Default gender
        output += f"- **Ethnicity**: Unknown\n"  # Default
        output += f"- **Clothing**: Professional attire\n"  # Default
        output += f"- **Expression**: Neutral\n"  # Default
        output += f"- **Attitude**: {npc.personality[:50]}\n"
        output += f"- **Details**: Standard appearance\n"  # Default
        output += f"- **Personality**: {npc.personality}\n"
        output += f"- **Relationships**: Interacts professionally with colleagues\n"  # Default
        output += f"- **Story Context**: {npc.story_context}\n"
        output += f"- **Information Known**:\n"
        output += f"  - `{npc.outcome_provided}` HIGH: Key information this NPC provides\n"
        output += f"- **Actions Available**:\n"
        output += f"  - (none)\n"
        output += f"- **Cover Story Options**:\n"
        output += f"  - `professional`: \"I have an appointment.\" -- (Checks schedule)\n"
        output += f"  - `delivery`: \"I'm delivering a package.\" -- (Asks for ID)\n"
        output += f"  - `alien`: \"I'm from outer space.\" -- (Confused look)\n\n"
    
    return output


def render_tasks(graph: ScenarioGraph) -> str:
    """Render tasks by role"""
    output = "## Roles & Tasks\n\n"
    
    # Group tasks by role
    tasks_by_role = defaultdict(list)
    for task in graph.tasks:
        tasks_by_role[task.role].append(task)
    
    # Render each role's tasks
    for role in graph.roles:
        role_name = role.replace('_', ' ').title()
        output += f"### {role_name}\n\n"
        output += f"**Tasks:**\n"
        
        role_tasks = tasks_by_role.get(role, [])
        for idx, task in enumerate(role_tasks, 1):
            output += self._render_single_task(idx, task)
        
        output += "\n"
    
    return output


def _render_single_task(idx: int, task: Task) -> str:
    """Render a single task"""
    # Map task type to emoji
    emoji_map = {
        'minigame': '🎮',
        'npc_llm': '💬',
        'search': '🔍',
        'handoff': '🤝',
        'info_share': '🗣️'
    }
    
    emoji = emoji_map.get(task.type, '❓')
    
    # Build task type display
    if task.type == 'minigame' and task.minigame_id:
        type_display = f"{emoji} {task.minigame_id}"
    else:
        type_display = f"{emoji} {task.type.upper()}"
    
    output = f"{idx}. **{task.id}. {type_display}** - {task.description}\n"
    output += f"    - *Description:* {task.description}\n"
    
    # Add type-specific fields
    if task.type == 'npc_llm' and task.npc_id:
        output += f"    - *NPC:* `{task.npc_id}`\n"
        if task.target_outcome:
            output += f"    - *Target Outcomes:* `{task.target_outcome}`\n"
    
    elif task.type == 'search' and task.search_items:
        items_str = ', '.join([f'`{item}`' for item in task.search_items])
        output += f"    - *Search Items:* {items_str}\n"
    
    elif task.type == 'handoff':
        if task.handoff_item:
            output += f"    - *Handoff Item:* `{task.handoff_item}`\n"
        if task.handoff_to_role:
            output += f"    - *Handoff To:* {task.handoff_to_role.replace('_', ' ').title()}\n"
    
    elif task.type == 'info_share':
        if task.info_id:
            output += f"    - *Info:* `{task.info_id}`\n"
        if task.share_with:
            output += f"    - *Share With:* {task.share_with}\n"
    
    output += f"    - *Location:* `{task.location}`\n"
    
    # Render prerequisites
    if task.prerequisites:
        output += f"    - *Prerequisites:*\n"
        for prereq in task.prerequisites:
            prereq_type = prereq['type'].capitalize()
            prereq_id = prereq['id']
            output += f"        - {prereq_type} `{prereq_id}`\n"
    else:
        output += f"    - *Prerequisites:* None (starting task)\n"
    
    output += "\n"
    return output


def render_markdown(graph: ScenarioGraph) -> str:
    """
    Render complete markdown from scenario graph
    
    Args:
        graph: Validated ScenarioGraph
    
    Returns:
        Complete markdown string
    """
    output = ""
    
    output += render_header(graph)
    output += render_locations(graph)
    output += render_items(graph)
    output += render_npcs(graph)
    output += render_tasks(graph)
    
    return output


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Render markdown from graph (Stage 4)")
    parser.add_argument("graph_file", help="Path to JSON graph file")
    parser.add_argument("--output", help="Output markdown file path")
    
    args = parser.parse_args()
    
    print(f"📝 Rendering markdown from graph...")
    print(f"   Graph: {args.graph_file}")
    print()
    
    # Load graph
    graph_path = Path(args.graph_file)
    if not graph_path.exists():
        print(f"❌ Graph file not found: {graph_path}")
        sys.exit(1)
    
    graph_data = json.loads(graph_path.read_text())
    
    # Reconstruct graph (simple approach)
    # In production, add proper deserialization
    graph = ScenarioGraph(
        scenario_id=graph_data['scenario_id'],
        objective=graph_data['objective'],
        player_count=graph_data['player_count'],
        roles=graph_data['roles']
    )
    
    # Reconstruct locations
    for loc_data in graph_data.get('locations', []):
        graph.locations.append(Location(**loc_data))
    
    # Reconstruct items
    for item_data in graph_data.get('items', []):
        graph.items.append(Item(**item_data))
    
    # Reconstruct NPCs
    for npc_data in graph_data.get('npcs', []):
        graph.npcs.append(NPC(**npc_data))
    
    # Reconstruct tasks
    for task_data in graph_data.get('tasks', []):
        graph.tasks.append(Task(**task_data))
    
    # Render markdown
    markdown = render_markdown(graph)
    
    # Save to file
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = graph_path.with_suffix('.md')
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown)
    
    print(f"✅ Rendered markdown ({len(markdown.split())} words)")
    print(f"💾 Saved to: {output_path}")
