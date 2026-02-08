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
    PrerequisiteType,
    Prerequisite,
    Location,
    NPCData,
    NPCInfoItem,
    NPCAction,
    NPCCoverOption,
    Item
)

logger = logging.getLogger(__name__)


class ExperienceLoader:
    """
    Parses generated experience markdown files
    
    Markdown format example:
    ### Hacker
    **Tasks:**
    1. **🎮 wire_connecting** - Prep Hacking Device
       - Assemble and configure the specialized hacking device at the crew hideout.
       - *Location:* Crew Hideout
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
        
        # Extract items
        items_by_location = self._extract_items(content)
        
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
            items_by_location=items_by_location,
            timeline_minutes=120,
            elapsed_minutes=0
        )
        
        total_items = sum(len(items) for items in items_by_location.values())
        logger.info(f"Loaded experience: {len(tasks)} tasks, {len(npcs)} NPCs, {len(locations)} locations, {total_items} items")
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
        # Use greedy match to capture all content until next ## section
        locations_match = re.search(r'## Locations\s*\n(.*?)(?=^##\s|\Z)', content, re.DOTALL | re.MULTILINE)
        if not locations_match:
            logger.warning("No ## Locations section found")
            return locations
        
        locations_text = locations_match.group(1)
        logger.debug(f"Locations section length: {len(locations_text)} chars")
        
        # Parse each location subsection
        for section_match in re.finditer(r'### (.+?)\n(.*?)(?=\n###|$)', locations_text, re.DOTALL):
            category = section_match.group(1).strip()
            section_content = section_match.group(2)
            
            # Extract individual locations with explicit IDs
            # New format: - **ID**: `location_id`
            #             - **Name**: Location Name
            #             - **Description**: Description text
            #             - **Visual**: visual description
            location_blocks = re.split(r'(?=^\s*-\s+\*\*ID\*\*:)', section_content, flags=re.MULTILINE)
            
            for block in location_blocks:
                if not block.strip():
                    continue
                
                # Extract ID (required)
                id_match = re.search(r'-\s+\*\*ID\*\*:\s*`?([a-z_]+)`?', block, re.IGNORECASE)
                if not id_match:
                    continue
                
                loc_id = id_match.group(1).strip()
                
                # Extract name (required)
                name_match = re.search(r'-\s+\*\*Name\*\*:\s*(.+?)(?=\n|$)', block)
                if not name_match:
                    continue
                name = name_match.group(1).strip()
                
                # Extract description (required)
                desc_match = re.search(r'-\s+\*\*Description\*\*:\s*(.+?)(?=\n\s*-|$)', block, re.DOTALL)
                description = desc_match.group(1).strip() if desc_match else ""
                
                # Extract visual description if present
                visual_match = re.search(r'-\s+\*\*Visual\*\*:\s*(.+?)(?=\n\s*$|$)', block, re.DOTALL)
                visual = visual_match.group(1).strip() if visual_match else ""
                
                locations.append(Location(
                    id=loc_id,
                    name=name,
                    description=description,
                    category=category,
                    visual=visual
                ))
        
        return locations
    
    def _extract_npcs(self, content: str) -> List[NPCData]:
        """Extract NPC data from structured NPC section"""
        npcs = []
        
        # Find the NPCs section (stop at next ## but not ###)
        npcs_match = re.search(r'## NPCs\s*\n(.*?)(?=\n## (?!#)|\Z)', content, re.DOTALL)
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
            
            # Extract visual fields for image generation
            gender_match = re.search(r'-\s*\*\*Gender\*\*:\s*(.+)', block)
            gender = gender_match.group(1).strip() if gender_match else "person"
            
            ethnicity_match = re.search(r'-\s*\*\*Ethnicity\*\*:\s*(.+)', block)
            ethnicity = ethnicity_match.group(1).strip() if ethnicity_match else ""
            
            clothing_match = re.search(r'-\s*\*\*Clothing\*\*:\s*(.+)', block)
            clothing = clothing_match.group(1).strip() if clothing_match else ""
            
            expression_match = re.search(r'-\s*\*\*Expression\*\*:\s*(.+)', block)
            expression = expression_match.group(1).strip() if expression_match else "friendly"
            
            attitude_match = re.search(r'-\s*\*\*Attitude\*\*:\s*(.+)', block)
            attitude = attitude_match.group(1).strip() if attitude_match else "approachable"
            
            details_match = re.search(r'-\s*\*\*Details\*\*:\s*(.+)', block)
            details = details_match.group(1).strip() if details_match else ""
            
            # Extract structured information known
            information_known = self._extract_npc_info_items(block)
            
            # Extract actions available
            actions_available = self._extract_npc_actions(block)
            
            # Extract cover story options
            cover_options = self._extract_npc_cover_options(block)
            
            npc = NPCData(
                id=npc_id,
                name=name,
                role=role,
                personality=personality,
                location=location,
                gender=gender,
                ethnicity=ethnicity,
                clothing=clothing,
                expression=expression,
                attitude=attitude,
                details=details,
                information_known=information_known,
                actions_available=actions_available,
                cover_options=cover_options,
            )
            npcs.append(npc)
            logger.debug(f"Parsed NPC: {name} ({role}) at {location} - {len(information_known)} info items, {len(actions_available)} actions, {len(cover_options)} covers")
        
        return npcs
    
    def _extract_npc_info_items(self, block: str) -> List[NPCInfoItem]:
        """Extract structured info items from NPC block
        
        Format:
          - `vault_location` HIGH: Description text
          - MEDIUM: Description text (no ID = flavor only)
        """
        items = []
        
        # Find Information Known section
        info_match = re.search(r'-\s*\*\*Information Known\*\*:\s*\n(.*?)(?=\n-\s*\*\*|\Z)', block, re.DOTALL)
        if not info_match:
            return items
        
        info_text = info_match.group(1)
        
        for line in info_text.strip().split('\n'):
            line = line.strip()
            if not line.startswith('-'):
                continue
            line = line.lstrip('- ').strip()
            
            # Try format with ID: `info_id` CONFIDENCE: description
            id_match = re.match(r'`(\w+)`\s+(HIGH|MEDIUM|LOW|VERY HIGH):\s*(.+)', line)
            if id_match:
                items.append(NPCInfoItem(
                    info_id=id_match.group(1),
                    confidence=id_match.group(2),
                    description=id_match.group(3).strip()
                ))
            else:
                # Format without ID: CONFIDENCE: description (flavor only)
                no_id_match = re.match(r'(HIGH|MEDIUM|LOW|VERY HIGH):\s*(.+)', line)
                if no_id_match:
                    items.append(NPCInfoItem(
                        info_id=None,
                        confidence=no_id_match.group(1),
                        description=no_id_match.group(2).strip()
                    ))
        
        return items
    
    def _extract_npc_actions(self, block: str) -> List[NPCAction]:
        """Extract actions available from NPC block
        
        Format:
          - `leave_post` HIGH: Description text
        """
        actions = []
        
        # Find Actions Available section
        actions_match = re.search(r'-\s*\*\*Actions Available\*\*:\s*\n(.*?)(?=\n-\s*\*\*|\Z)', block, re.DOTALL)
        if not actions_match:
            return actions
        
        actions_text = actions_match.group(1)
        
        for line in actions_text.strip().split('\n'):
            line = line.strip()
            if not line.startswith('-'):
                continue
            line = line.lstrip('- ').strip()
            
            # Format: `action_id` CONFIDENCE: description
            action_match = re.match(r'`(\w+)`\s+(HIGH|MEDIUM|LOW|VERY HIGH):\s*(.+)', line)
            if action_match:
                actions.append(NPCAction(
                    action_id=action_match.group(1),
                    confidence=action_match.group(2),
                    description=action_match.group(3).strip()
                ))
        
        return actions
    
    def _extract_npc_cover_options(self, block: str) -> List[NPCCoverOption]:
        """Extract cover story options from NPC block
        
        Format:
          - `cover_id`: "Description text" -- Trust: LEVEL (explanation)
        """
        covers = []
        
        # Find Cover Story Options section
        covers_match = re.search(r'-\s*\*\*Cover Story Options\*\*:\s*\n(.*?)(?=\n-\s*\*\*|\n###|\Z)', block, re.DOTALL)
        if not covers_match:
            return covers
        
        covers_text = covers_match.group(1)
        
        for line in covers_text.strip().split('\n'):
            line = line.strip()
            if not line.startswith('-'):
                continue
            line = line.lstrip('- ').strip()
            
            # Format: `cover_id`: "description" -- Trust: LEVEL (explanation)
            cover_match = re.match(r'`(\w+)`:\s*"(.+?)"\s*--\s*Trust:\s*(HIGH|MEDIUM|LOW)\s*\((.+?)\)', line)
            if cover_match:
                covers.append(NPCCoverOption(
                    cover_id=cover_match.group(1),
                    description=cover_match.group(2).strip(),
                    trust_level=cover_match.group(3).lower(),
                    trust_description=cover_match.group(4).strip()
                ))
        
        return covers
    
    def _extract_items(self, content: str) -> Dict[str, List[Item]]:
        """Extract items by location from ## Items by Location section"""
        items_by_location = {}
        
        # Find the Items by Location section
        items_match = re.search(r'## Items by Location\s*\n(.*?)(?=\n## (?!#)|\Z)', content, re.DOTALL)
        if not items_match:
            logger.warning("No Items by Location section found in experience file")
            return items_by_location
        
        items_section = items_match.group(1)
        
        # Parse each location (starts with ###)
        location_blocks = re.split(r'(?=### )', items_section)
        
        for block in location_blocks:
            if not block.strip():
                continue
            
            # Extract location name from header
            location_match = re.search(r'###\s+(.+)', block)
            if not location_match:
                continue
            
            location_name = location_match.group(1).strip()
            items = []
            
            # Parse each item (starts with - **ID**)
            item_blocks = re.split(r'(?=- \*\*ID\*\*)', block)
            
            for item_block in item_blocks:
                if not item_block.strip() or '**ID**' not in item_block:
                    continue
                
                # Extract ID
                id_match = re.search(r'-\s*\*\*ID\*\*:\s*`([^`]+)`', item_block)
                if not id_match:
                    continue
                item_id = id_match.group(1)
                
                # Extract Name
                name_match = re.search(r'-\s*\*\*Name\*\*:\s*(.+)', item_block)
                name = name_match.group(1).strip() if name_match else item_id
                
                # Extract Description
                desc_match = re.search(r'-\s*\*\*Description\*\*:\s*(.+)', item_block)
                description = desc_match.group(1).strip() if desc_match else ""
                
                # Extract Visual description
                visual_match = re.search(r'-\s*\*\*Visual\*\*:\s*(.+?)(?=\n\s*-\s*\*\*|\Z)', item_block, re.DOTALL)
                visual = visual_match.group(1).strip() if visual_match else ""
                
                # Extract Required For
                req_match = re.search(r'-\s*\*\*Required For\*\*:\s*(.+)', item_block)
                required_for = req_match.group(1).strip() if req_match else None
                if required_for and required_for.lower() == 'none':
                    required_for = None
                
                # Extract Hidden
                hidden_match = re.search(r'-\s*\*\*Hidden\*\*:\s*(true|false)', item_block, re.IGNORECASE)
                hidden = hidden_match and hidden_match.group(1).lower() == 'true'
                
                item = Item(
                    id=item_id,
                    name=name,
                    description=description,
                    visual=visual,
                    location=location_name,
                    required_for=required_for,
                    hidden=hidden
                )
                items.append(item)
                logger.debug(f"Parsed item: {name} at {location_name}")
            
            if items:
                items_by_location[location_name] = items
        
        return items_by_location
    
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
            
            # Try to extract explicit task ID from header (e.g., "MM1. 💬 NPC_LLM")
            explicit_id_match = re.match(r'([A-Z]{1,3}\d+)\.\s+', task_emoji_and_type)
            if explicit_id_match:
                task_id = explicit_id_match.group(1)
            else:
                task_id = f"{role_code}{task_num}"
            
            # Parse task type from emoji
            task_type = TaskType.MINIGAME  # default
            for emoji, ttype in self.TASK_TYPE_MAP.items():
                if emoji in task_emoji_and_type:
                    task_type = ttype
                    break
            
            # Extract metadata
            location = self._extract_field(task_details, "Location")
            prerequisites = self._extract_prerequisites(task_details)
            # Also extract legacy dependencies for backward compatibility
            dependencies = self._extract_dependencies(task_details)
            target_outcomes = self._extract_target_outcomes(task_details)
            
            # Create task
            task = Task(
                id=task_id,
                type=task_type,
                description=task_description,
                assigned_role=role,
                location=location or "Unknown",
                status=TaskStatus.LOCKED,
                prerequisites=prerequisites,
                dependencies=dependencies,
                target_outcomes=target_outcomes,
            )
            
            # Add type-specific metadata
            if task_type == TaskType.MINIGAME:
                # Extract minigame ID from emoji line
                minigame_match = re.search(r'🎮\s+(\w+)', task_emoji_and_type)
                if minigame_match:
                    task.minigame_id = minigame_match.group(1)
            
            elif task_type == TaskType.NPC_LLM:
                # Extract NPC ID (format: *NPC:* `npc_id` (NPC Name))
                npc_id_match = re.search(r'\*NPC:\*\s*`([^`]+)`', task_details)
                if npc_id_match:
                    task.npc_id = npc_id_match.group(1).strip()
                    # Also extract NPC name from parenthetical
                    npc_name_match = re.search(r'\*NPC:\*\s*`[^`]+`\s*\((.+?)\)', task_details)
                    if npc_name_match:
                        task.npc_name = npc_name_match.group(1).strip()
                else:
                    # Fallback to old format: *NPC: Name (personality)*
                    npc_match = re.search(r'\*NPC:\s*(.+?)\s*\((.+?)\)', task_details)
                    if npc_match:
                        task.npc_name = npc_match.group(1).strip()
                        task.npc_personality = npc_match.group(2).strip()
                        task.npc_id = task.npc_name.lower().replace(" ", "_")
            
            elif task_type == TaskType.SEARCH:
                # Extract items to find (new format: *Search Items:* item1, item2)
                search_match = re.search(r'\*Search Items:\*\s*(.+?)(?:\n|$)', task_details)
                if search_match:
                    items = [item.strip() for item in search_match.group(1).split(',')]
                    task.search_items = items
                else:
                    # Fallback to old format: *Find: items*
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
    
    def _extract_prerequisites(self, text: str) -> List[Prerequisite]:
        """Extract typed prerequisites from Prerequisites field
        
        Formats:
          - *Prerequisites:* None (starting task)
          - *Prerequisites:*
            - Task `MM1` (description)
            - Outcome `vault_location` (description)
            - Item `safe_cracking_tools` (description)
        """
        prereqs = []
        
        # Find Prerequisites section (multi-line)
        prereq_match = re.search(r'\*Prerequisites:\*\s*(.*?)(?=\n\s*\n|\n\s*\d+\.|\Z)', text, re.DOTALL)
        if not prereq_match:
            return prereqs
        
        prereq_text = prereq_match.group(1).strip()
        
        # Check for None
        if "None" in prereq_text or "starting task" in prereq_text.lower():
            return prereqs
        
        # Parse each prerequisite line
        type_map = {
            'task': PrerequisiteType.TASK,
            'outcome': PrerequisiteType.OUTCOME,
            'item': PrerequisiteType.ITEM,
        }
        
        for line in prereq_text.split('\n'):
            line = line.strip()
            if not line.startswith('-'):
                # Could be single-line format: Task `MM1` (description)
                if line:
                    single_match = re.match(r'(Task|Outcome|Item)\s+`(\w+)`\s*(?:\((.+?)\))?', line, re.IGNORECASE)
                    if single_match:
                        ptype = type_map.get(single_match.group(1).lower())
                        if ptype:
                            prereqs.append(Prerequisite(
                                type=ptype,
                                id=single_match.group(2),
                                description=single_match.group(3) if single_match.group(3) else None
                            ))
                continue
            
            line = line.lstrip('- ').strip()
            
            # Format: Type `id` (description)
            prereq_line_match = re.match(r'(Task|Outcome|Item)\s+`(\w+)`\s*(?:\((.+?)\))?', line, re.IGNORECASE)
            if prereq_line_match:
                ptype = type_map.get(prereq_line_match.group(1).lower())
                if ptype:
                    prereqs.append(Prerequisite(
                        type=ptype,
                        id=prereq_line_match.group(2),
                        description=prereq_line_match.group(3) if prereq_line_match.group(3) else None
                    ))
        
        return prereqs
    
    def _extract_dependencies(self, text: str) -> List[str]:
        """Extract task dependencies - supports both old and new formats.
        
        Old format: *Dependencies:* `MM1` (description)
        New format: *Prerequisites:* Task `MM1` (description)
        
        Returns only task IDs for legacy compatibility.
        """
        # First try new Prerequisites format
        prereqs = self._extract_prerequisites(text)
        if prereqs:
            return [p.id for p in prereqs if p.type == PrerequisiteType.TASK]
        
        # Fall back to old Dependencies format
        deps_text = self._extract_field(text, "Dependencies")
        if not deps_text:
            return []
        
        # Check for "None" or "Starting task"
        if "None" in deps_text or "Starting task" in deps_text.lower():
            return []
        
        # Extract task IDs in backticks or parentheses
        dependencies = []
        # Try backtick format first: `MM1`
        for match in re.finditer(r'`([A-Z]{1,3}\d+)`', deps_text):
            dependencies.append(match.group(1))
        
        if not dependencies:
            # Fallback to parentheses format: (MM1)
            for match in re.finditer(r'\(([A-Z]{1,3}\d+)\)', deps_text):
                dependencies.append(match.group(1))
        
        return dependencies
    
    def _extract_target_outcomes(self, text: str) -> List[str]:
        """Extract target outcomes for NPC tasks
        
        Format: *Target Outcomes:* `vault_location`, `patrol_schedule`
        """
        outcomes_text = self._extract_field(text, "Target Outcomes")
        if not outcomes_text:
            return []
        
        # Extract IDs from backticks
        outcomes = []
        for match in re.finditer(r'`(\w+)`', outcomes_text):
            outcomes.append(match.group(1))
        
        return outcomes
    
    def _set_initial_statuses(self, tasks: Dict[str, Task]) -> None:
        """Set initial task statuses (tasks with no prerequisites/dependencies are AVAILABLE)"""
        for task in tasks.values():
            has_prereqs = len(task.prerequisites) > 0 or len(task.dependencies) > 0
            if not has_prereqs:
                task.status = TaskStatus.AVAILABLE
                logger.debug(f"Task {task.id} is initially available")
            else:
                task.status = TaskStatus.LOCKED
