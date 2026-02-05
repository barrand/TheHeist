"""
Experience Loader Service
Parses generated experience markdown files into GameState objects
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from app.models.game_state import (
    GameState,
    Task,
    TaskType,
    TaskStatus,
    Location,
    NPCData
)

logger = logging.getLogger(__name__)


class ExperienceLoader:
    """
    Parses generated experience markdown files
    
    Markdown format example:
    ### Hacker
    **Tasks:**
    1. **🎮 wire_connecting** - Prep Hacking Device
       - Assemble and configure the specialized hacking device at the safe house.
       - *Location:* Safe House
       - *Dependencies:* None (Starting task)
    """
    
    # Task type emoji mapping
    TASK_TYPE_MAP = {
        "🎮": TaskType.MINIGAME,
        "💬": TaskType.NPC_LLM,
        "🔍": TaskType.SEARCH,
        "🤝": TaskType.HANDOFF,
        "🗣️": TaskType.INFO_SHARE,
        "🎯": TaskType.DISCOVERY,
    }
    
    # Role code mapping (for task IDs)
    ROLE_CODES = {
        "mastermind": "MM",
        "hacker": "H",
        "safe_cracker": "SC",
        "safe cracker": "SC",
        "insider": "I",
        "driver": "D",
        "grifter": "G",
        "muscle": "M",
        "lookout": "L",
        "fence": "F",
        "cat_burglar": "CB",
        "cat burglar": "CB",
        "cleaner": "CL",
        "pickpocket": "PP",
    }
    
    def __init__(self, experiences_dir: str = "examples"):
        """
        Initialize loader
        
        Args:
            experiences_dir: Directory containing experience markdown files
        """
        self.experiences_dir = Path(experiences_dir)
        logger.info(f"ExperienceLoader initialized (dir: {experiences_dir})")
    
    def load_experience(self, scenario: str, selected_roles: List[str]) -> GameState:
        """
        Load and parse an experience file
        
        Args:
            scenario: Scenario ID (e.g., "museum_gala_vault")
            selected_roles: List of roles players selected
            
        Returns:
            Parsed GameState
        """
        # Find the markdown file
        # Format: generated_{scenario}_{player_count}players.md
        player_count = len(selected_roles)
        filename = f"generated_{scenario}_{player_count}players.md"
        filepath = self.experiences_dir / filename
        
        if not filepath.exists():
            logger.error(f"Experience file not found: {filepath}")
            raise FileNotFoundError(f"Experience file not found: {filename}")
        
        logger.info(f"Loading experience from {filepath}")
        
        # Parse the markdown
        with open(filepath, 'r') as f:
            content = f.read()
        
        return self._parse_markdown(content, scenario, selected_roles)
    
    def _parse_markdown(self, content: str, scenario: str, selected_roles: List[str]) -> GameState:
        """Parse markdown content into GameState"""
        
        # Extract objective
        objective = self._extract_objective(content)
        
        # Extract locations
        locations = self._extract_locations(content)
        
        # Extract NPCs
        npcs = self._extract_npcs(content)
        
        # Extract tasks for each role
        tasks = {}
        for role in selected_roles:
            role_tasks = self._extract_role_tasks(content, role)
            tasks.update(role_tasks)
        
        # Set initial task statuses
        self._set_initial_statuses(tasks)
        
        game_state = GameState(
            objective=objective,
            scenario=scenario,
            locations=locations,
            tasks=tasks,
            npcs=npcs,
            timeline_minutes=120,
            elapsed_minutes=0
        )
        
        logger.info(f"Loaded experience: {len(tasks)} tasks, {len(npcs)} NPCs, {len(locations)} locations")
        return game_state
    
    def _extract_objective(self, content: str) -> str:
        """Extract main objective from markdown"""
        match = re.search(r'## Objective\s*\n(.+)', content)
        if match:
            return match.group(1).strip()
        return "Complete the heist successfully"
    
    def _extract_locations(self, content: str) -> List[Location]:
        """Extract locations from markdown"""
        locations = []
        
        # Find the Locations section
        locations_match = re.search(r'## Locations\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not locations_match:
            return locations
        
        locations_text = locations_match.group(1)
        
        # Parse each location subsection
        for section_match in re.finditer(r'### (.+?)\n(.*?)(?=\n###|\Z)', locations_text, re.DOTALL):
            category = section_match.group(1).strip()
            section_content = section_match.group(2)
            
            # Extract individual locations (lines starting with -)
            for loc_match in re.finditer(r'-\s+\*\*(.+?)\*\*:(.+)', section_content):
                name = loc_match.group(1).strip()
                description = loc_match.group(2).strip()
                
                loc_id = name.lower().replace(" ", "_").replace("'", "")
                locations.append(Location(
                    id=loc_id,
                    name=name,
                    description=description,
                    category=category
                ))
        
        return locations
    
    def _extract_npcs(self, content: str) -> List[NPCData]:
        """Extract NPC data from structured NPC section"""
        npcs = []
        
        # Find the NPCs section
        npcs_match = re.search(r'## NPCs\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not npcs_match:
            logger.warning("No NPCs section found in experience file")
            return npcs
        
        npcs_section = npcs_match.group(1)
        
        # Parse each NPC (starts with ###)
        npc_blocks = re.split(r'(?=### )', npcs_section)
        
        for block in npc_blocks:
            if not block.strip():
                continue
            
            # Extract NPC name and role from header (format: ### Role - Name)
            header_match = re.search(r'###\s+(.+?)\s+-\s+(.+)', block)
            if not header_match:
                continue
            
            role = header_match.group(1).strip()
            name = header_match.group(2).strip()
            
            # Extract ID
            id_match = re.search(r'-\s*\*\*ID\*\*:\s*`([^`]+)`', block)
            npc_id = id_match.group(1) if id_match else name.lower().replace(" ", "_")
            
            # Extract location
            location_match = re.search(r'-\s*\*\*Location\*\*:\s*(.+)', block)
            location = location_match.group(1).strip() if location_match else "Unknown"
            
            # Extract personality
            personality_match = re.search(r'-\s*\*\*Personality\*\*:\s*(.+)', block)
            personality = personality_match.group(1).strip() if personality_match else "Friendly and helpful"
            
            npc = NPCData(
                id=npc_id,
                name=name,
                role=role,
                personality=personality,
                location=location
            )
            npcs.append(npc)
            logger.debug(f"Parsed NPC: {name} ({role}) at {location}")
        
        return npcs
    
    def _extract_role_tasks(self, content: str, role: str) -> Dict[str, Task]:
        """Extract all tasks for a specific role"""
        tasks = {}
        
        # Find the role section
        role_display = role.replace("_", " ").title()
        role_pattern = f'### {role_display}\\s*\\n\\*\\*Tasks:\\*\\*(.*?)(?=\\n###|\\n---\\n|\\Z)'
        role_match = re.search(role_pattern, content, re.DOTALL)
        
        if not role_match:
            logger.warning(f"Role section not found for {role}")
            return tasks
        
        role_content = role_match.group(1)
        role_code = self.ROLE_CODES.get(role.lower(), "X")
        
        # Extract each numbered task
        task_pattern = r'(\d+)\.\s+\*\*(.+?)\*\*\s+-\s+(.+?)\n(.*?)(?=\n\d+\.\s+\*\*|\Z)'
        
        for task_match in re.finditer(task_pattern, role_content, re.DOTALL):
            task_num = task_match.group(1)
            task_emoji_and_type = task_match.group(2).strip()
            task_description = task_match.group(3).strip()
            task_details = task_match.group(4).strip()
            
            task_id = f"{role_code}{task_num}"
            
            # Parse task type from emoji
            task_type = TaskType.MINIGAME  # default
            for emoji, ttype in self.TASK_TYPE_MAP.items():
                if emoji in task_emoji_and_type:
                    task_type = ttype
                    break
            
            # Extract metadata
            location = self._extract_field(task_details, "Location")
            dependencies = self._extract_dependencies(task_details)
            
            # Create task
            task = Task(
                id=task_id,
                type=task_type,
                description=task_description,
                assigned_role=role,
                location=location or "Unknown",
                status=TaskStatus.LOCKED,
                dependencies=dependencies
            )
            
            # Add type-specific metadata
            if task_type == TaskType.MINIGAME:
                # Extract minigame ID from emoji line
                minigame_match = re.search(r'🎮\s+(\w+)', task_emoji_and_type)
                if minigame_match:
                    task.minigame_id = minigame_match.group(1)
            
            elif task_type == TaskType.NPC_LLM:
                # Extract NPC ID (new format: *NPC:* `npc_id`)
                npc_id_match = re.search(r'\*NPC:\*\s*`([^`]+)`', task_details)
                if npc_id_match:
                    task.npc_id = npc_id_match.group(1).strip()
                else:
                    # Fallback to old format: *NPC: Name (personality)*
                    npc_match = re.search(r'\*NPC:\s*(.+?)\s*\((.+?)\)', task_details)
                    if npc_match:
                        task.npc_name = npc_match.group(1).strip()
                        task.npc_personality = npc_match.group(2).strip()
                        task.npc_id = task.npc_name.lower().replace(" ", "_")
            
            elif task_type == TaskType.SEARCH:
                # Extract items to find
                find_match = re.search(r'\*Find:\s*(.+?)\*', task_details)
                if find_match:
                    items = [item.strip() for item in find_match.group(1).split(',')]
                    task.search_items = items
            
            elif task_type == TaskType.HANDOFF:
                # Extract item and recipient from description
                handoff_match = re.search(r'🤝\s+(\w+)', task_emoji_and_type)
                if handoff_match:
                    task.handoff_item = handoff_match.group(1)
                
                # Try to extract recipient from arrow in description
                if "→" in task_description:
                    task.handoff_to_role = "specific_player"
                elif "←" in task_description:
                    task.handoff_to_role = "receive"
            
            tasks[task_id] = task
        
        logger.info(f"Extracted {len(tasks)} tasks for role: {role}")
        return tasks
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a metadata field from task details"""
        pattern = f'\\*{field_name}:\\*\\s*(.+?)(?:\\n|$)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_dependencies(self, text: str) -> List[str]:
        """Extract task dependencies from Dependencies field"""
        deps_text = self._extract_field(text, "Dependencies")
        if not deps_text:
            return []
        
        # Check for "None" or "Starting task"
        if "None" in deps_text or "Starting task" in deps_text.lower():
            return []
        
        # Extract task IDs in parentheses (e.g., "Briefing complete (MM1)")
        dependencies = []
        for match in re.finditer(r'\(([A-Z]{1,3}\d+)\)', deps_text):
            dependencies.append(match.group(1))
        
        return dependencies
    
    def _set_initial_statuses(self, tasks: Dict[str, Task]) -> None:
        """Set initial task statuses (tasks with no dependencies are AVAILABLE)"""
        for task in tasks.values():
            if len(task.dependencies) == 0:
                task.status = TaskStatus.AVAILABLE
                logger.debug(f"Task {task.id} is initially available")
            else:
                task.status = TaskStatus.LOCKED
