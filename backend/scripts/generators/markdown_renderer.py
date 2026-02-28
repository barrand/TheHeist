"""
Markdown Renderer
Converts procedural scenario graphs to human-readable markdown format
"""

import json
from pathlib import Path
from collections import defaultdict


def render_markdown(graph) -> str:
    """
    Render complete markdown from scenario graph
    
    Args:
        graph: ScenarioGraph from procedural_generator
    
    Returns:
        Complete markdown string
    """
    output = ""
    
    output += _render_header(graph)
    output += _render_locations(graph)
    output += _render_items(graph)
    output += _render_npcs(graph)
    output += _render_tasks(graph)
    
    return output


def _render_header(graph) -> str:
    """Render scenario header"""
    # Determine roles from tasks
    roles = sorted(set(task.assigned_role for task in graph.tasks))
    role_names = ', '.join([r.replace('_', ' ').title() for r in roles])
    player_count = len(roles)
    
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
**Player Count**: {player_count} players

## Objective
{graph.objective}

"""


def _render_locations(graph) -> str:
    """Render locations section"""
    output = "## Locations\n\n"
    
    # Group by category
    locations_by_category = defaultdict(list)
    for location in graph.locations:
        locations_by_category[location.category].append(location)
    
    for category, locations in sorted(locations_by_category.items()):
        output += f"### {category}\n"
        for location in locations:
            output += f"- **{location.name}** (`{location.id}`): {location.description}\n"
        output += "\n"
    
    output += f"**Total Locations**: {len(graph.locations)}\n\n"
    return output


def _render_items(graph) -> str:
    """Render items by location"""
    output = "## Items by Location\n\n"
    
    # Group items by location
    items_by_loc = defaultdict(list)
    for item in graph.items:
        items_by_loc[item.location].append(item)
    
    # Get location names
    loc_names = {loc.id: loc.name for loc in graph.locations}
    
    for loc_id in sorted(items_by_loc.keys()):
        items = items_by_loc[loc_id]
        loc_name = loc_names.get(loc_id, loc_id.replace('_', ' ').title())
        output += f"### {loc_name}\n"
        
        for item in items:
            output += f"- **{item.name}** (`{item.id}`)\n"
            output += f"  - **Description**: {item.description}\n"
            output += f"  - **Visual**: {item.visual or item.description}\n"
            
            if item.required_for:
                output += f"  - **Required For**: `{item.required_for}`\n"
            
            output += f"  - **Hidden**: {'true' if item.hidden else 'false'}\n"
            
            if item.unlock_prerequisites:
                output += f"  - **Unlock**:\n"
                for prereq in item.unlock_prerequisites:
                    prereq_type = prereq.type.capitalize()
                    output += f"    - {prereq_type} `{prereq.id}`\n"
            
            output += "\n"
    
    return output


def _render_npcs(graph) -> str:
    """Render NPCs section"""
    output = "## NPCs\n\n"
    
    for npc in graph.npcs:
        output += f"### {npc.role} - {npc.name}\n"
        output += f"- **ID**: `{npc.id}`\n"
        output += f"- **Role**: {npc.role}\n"
        output += f"- **Location**: `{npc.location}`\n"
        output += f"- **Age**: {getattr(npc, 'age', 35)}\n"
        output += f"- **Gender**: {npc.gender}\n"
        output += f"- **Ethnicity**: {npc.ethnicity or 'Unknown'}\n"
        output += f"- **Clothing**: {npc.clothing or 'Professional attire'}\n"
        output += f"- **Expression**: {npc.expression}\n"
        output += f"- **Attitude**: {npc.attitude}\n"
        output += f"- **Details**: {npc.details or 'Standard appearance'}\n"
        output += f"- **Personality**: {npc.personality}\n"
        output += f"- **Relationships**: {npc.relationships or 'Interacts professionally with colleagues'}\n"
        output += f"- **Story Context**: {npc.story_context or 'Works at this location'}\n"
        
        output += f"- **Information Known**:\n"
        if npc.information_known:
            for info in npc.information_known:
                info_id_str = f"`{info.info_id}`" if info.info_id else "(flavor)"
                output += f"  - {info_id_str} {info.confidence}: {info.description}\n"
        else:
            output += f"  - (none)\n"
        
        output += f"- **Actions Available**:\n"
        if npc.actions_available:
            for action in npc.actions_available:
                output += f"  - `{action.action_id}` {action.confidence}: {action.description}\n"
        else:
            output += f"  - (none)\n"
        
        output += f"- **Cover Story Options**:\n"
        if npc.cover_options:
            for cover in npc.cover_options:
                reaction = f" -- {cover.npc_reaction}" if cover.npc_reaction else ""
                output += f"  - `{cover.cover_id}`: \"{cover.description}\"{reaction}\n"
        else:
            output += f"  - `direct`: \"I'm here on business.\" -- (Professional response)\n"
        
        output += "\n"
    
    return output


def _render_tasks(graph) -> str:
    """Render tasks by role"""
    output = "## Roles & Tasks\n\n"
    
    # Group tasks by role
    tasks_by_role = defaultdict(list)
    for task in graph.tasks:
        tasks_by_role[task.assigned_role].append(task)
    
    # Render each role's tasks
    for role in sorted(tasks_by_role.keys()):
        role_name = role.replace('_', ' ').title()
        output += f"### {role_name}\n\n"
        output += f"**Tasks:**\n\n"
        
        role_tasks = tasks_by_role[role]
        for idx, task in enumerate(role_tasks, 1):
            output += _render_single_task(idx, task)
        
        output += "\n"
    
    return output


def _render_single_task(idx: int, task) -> str:
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
    
    # Add type-specific fields
    if task.type == 'npc_llm':
        if task.npc_id:
            output += f"   - *NPC:* `{task.npc_id}`\n"
        if task.target_outcomes:
            outcomes_str = ', '.join([f'`{o}`' for o in task.target_outcomes])
            output += f"   - *Target Outcomes:* {outcomes_str}\n"
    
    elif task.type == 'search':
        if task.search_items:
            items_str = ', '.join([f'`{item}`' for item in task.search_items])
            output += f"   - *Search Items:* {items_str}\n"
    
    elif task.type == 'handoff':
        if task.handoff_item:
            output += f"   - *Handoff Item:* `{task.handoff_item}`\n"
        if task.handoff_to_role:
            output += f"   - *Handoff To:* {task.handoff_to_role.replace('_', ' ').title()}\n"
    
    elif task.type == 'info_share':
        if task.info_description:
            output += f"   - *Info:* {task.info_description}\n"
    
    output += f"   - *Location:* `{task.location}`\n"
    
    # Render prerequisites
    if task.prerequisites:
        output += f"   - *Prerequisites:*\n"
        for prereq in task.prerequisites:
            prereq_type = prereq.type.capitalize()
            prereq_id = prereq.id
            output += f"      - {prereq_type} `{prereq_id}`\n"
    else:
        output += f"   - *Prerequisites:* None (starting task)\n"
    
    output += "\n"
    return output


def export_to_markdown(graph, output_path: str = None, roles=None) -> str:
    """
    Export scenario graph to markdown file.

    Args:
        graph: ScenarioGraph instance
        output_path: Optional explicit path. If None, auto-generates from scenario+roles.
        roles: Explicit role list for cache-key filename. Falls back to task roles if omitted.

    Returns:
        Path to written markdown file
    """
    markdown = render_markdown(graph)
    
    # Determine output path
    if output_path is None:
        output_dir = Path(__file__).parent.parent.parent / "experiences"
        output_dir.mkdir(exist_ok=True)

        role_list = sorted(roles) if roles else sorted(
            set(task.assigned_role for task in graph.tasks)
        )
        roles_part = "_".join(role_list)
        output_path = output_dir / f"generated_{graph.scenario_id}_{roles_part}.md"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    return str(output_path)
