"""
Stage 2: Structure Extractor

Parses semi-structured story text and converts it to a validated JSON graph.
This is a deterministic parser that extracts entities and relationships.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class Location:
    """A location in the heist"""
    id: str
    name: str
    description: str


@dataclass
class Item:
    """An item that can be found or used"""
    id: str
    name: str
    location: str
    hidden: bool
    description: str
    needed_for: str
    unlock_prerequisites: List[str] = field(default_factory=list)  # Task IDs that must complete first


@dataclass
class NPC:
    """A non-player character"""
    id: str
    name: str
    location: str
    role: str
    personality: str
    outcome_provided: str  # The single outcome this NPC provides
    story_context: str


@dataclass
class Task:
    """A task that a player must complete"""
    id: str
    role: str
    type: str  # search, npc_llm, minigame, handoff, info_share
    location: str
    description: str
    prerequisites: List[Dict[str, str]] = field(default_factory=list)  # [{type: task|outcome|item, id: xxx}]
    
    # Type-specific fields
    minigame_id: Optional[str] = None
    npc_id: Optional[str] = None
    target_outcome: Optional[str] = None
    search_items: List[str] = field(default_factory=list)
    handoff_item: Optional[str] = None
    handoff_to_role: Optional[str] = None
    info_id: Optional[str] = None
    share_with: Optional[str] = None
    
    is_final: bool = False  # Marks completion of heist objective


@dataclass
class ScenarioGraph:
    """Complete scenario data structure"""
    scenario_id: str
    objective: str
    player_count: int
    roles: List[str]
    
    locations: List[Location] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)
    npcs: List[NPC] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


class StoryParser:
    """Parse semi-structured story text into JSON graph"""
    
    def __init__(self, story_text: str):
        self.story_text = story_text
        self.errors: List[str] = []
    
    def parse(self, scenario_id: str, roles: List[str]) -> ScenarioGraph:
        """
        Parse story text into structured graph
        
        Args:
            scenario_id: Scenario ID for the graph
            roles: List of role IDs
        
        Returns:
            ScenarioGraph object
        """
        graph = ScenarioGraph(
            scenario_id=scenario_id,
            objective="",
            player_count=len(roles),
            roles=roles
        )
        
        # Extract objective
        graph.objective = self._extract_objective()
        
        # Extract locations
        graph.locations = self._extract_locations()
        
        # Extract items
        graph.items = self._extract_items()
        
        # Extract NPCs
        graph.npcs = self._extract_npcs()
        
        # Extract tasks
        graph.tasks = self._extract_tasks()
        
        return graph
    
    def _extract_objective(self) -> str:
        """Extract OBJECTIVE line"""
        match = re.search(r'OBJECTIVE:\s*(.+)', self.story_text)
        if match:
            return match.group(1).strip()
        return "Complete the heist"
    
    def _extract_locations(self) -> List[Location]:
        """Extract all LOCATION entries"""
        locations = []
        
        # Find LOCATIONS section
        locations_section = re.search(
            r'LOCATIONS:(.*?)(?=\n(?:ITEMS|NPCS|TASKS):|$)',
            self.story_text,
            re.DOTALL
        )
        
        if not locations_section:
            self.errors.append("No LOCATIONS section found")
            return locations
        
        section_text = locations_section.group(1)
        
        # Parse each location
        # Pattern: - LOCATION: Name [id]\n  DESC: description
        location_blocks = re.finditer(
            r'- LOCATION:\s*(.+?)\s*\[([^\]]+)\]\s*\n\s*DESC:\s*(.+?)(?=\n- LOCATION:|\n\n|$)',
            section_text,
            re.DOTALL
        )
        
        for match in location_blocks:
            name = match.group(1).strip()
            loc_id = match.group(2).strip()
            description = match.group(3).strip()
            
            locations.append(Location(
                id=loc_id,
                name=name,
                description=description
            ))
        
        return locations
    
    def _extract_items(self) -> List[Item]:
        """Extract all ITEM entries"""
        items = []
        
        # Find ITEMS section
        items_section = re.search(
            r'ITEMS:(.*?)(?=\n(?:NPCS|TASKS):|$)',
            self.story_text,
            re.DOTALL
        )
        
        if not items_section:
            self.errors.append("No ITEMS section found")
            return items
        
        section_text = items_section.group(1)
        
        # Parse each item
        # Pattern: - ITEM: Name [id]\n  AT: location\n  HIDDEN: bool\n  DESC: desc\n  NEEDED_FOR: purpose\n  UNLOCK: condition
        item_blocks = re.finditer(
            r'- ITEM:\s*(.+?)\s*\[([^\]]+)\]\s*\n\s*AT:\s*(.+?)\n\s*HIDDEN:\s*(true|false)\s*\n\s*DESC:\s*(.+?)\n\s*NEEDED_FOR:\s*(.+?)\n\s*UNLOCK:\s*(.+?)(?=\n- ITEM:|\n\n|$)',
            section_text,
            re.DOTALL
        )
        
        for match in item_blocks:
            name = match.group(1).strip()
            item_id = match.group(2).strip()
            location = match.group(3).strip()
            hidden = match.group(4).strip().lower() == 'true'
            description = match.group(5).strip()
            needed_for = match.group(6).strip()
            unlock_text = match.group(7).strip()
            
            # Parse unlock prerequisites
            unlock_prereqs = []
            if unlock_text.lower() != 'none':
                # Extract task IDs from unlock text
                task_matches = re.findall(r'Task\s+([A-Z]+\d+[a-z]?)', unlock_text)
                unlock_prereqs.extend(task_matches)
            
            items.append(Item(
                id=item_id,
                name=name,
                location=location,
                hidden=hidden,
                description=description,
                needed_for=needed_for,
                unlock_prerequisites=unlock_prereqs
            ))
        
        return items
    
    def _extract_npcs(self) -> List[NPC]:
        """Extract all NPC entries"""
        npcs = []
        
        # Find NPCS section
        npcs_section = re.search(
            r'NPCS:(.*?)(?=\nTASKS:|$)',
            self.story_text,
            re.DOTALL
        )
        
        if not npcs_section:
            self.errors.append("No NPCS section found")
            return npcs
        
        section_text = npcs_section.group(1)
        
        # Parse each NPC with more flexible regex
        # Pattern: - NPC: Name [id]\n  AT: location\n  ROLE: role\n  PERSONALITY: text\n  PROVIDES: outcome_id ...\n  STORY_CONTEXT: text
        npc_blocks = re.finditer(
            r'- NPC:\s*(.+?)\s*\[([^\]]+)\]\s*\n\s*AT:\s*(.+?)\n\s*ROLE:\s*(.+?)\n\s*PERSONALITY:\s*(.+?)\n\s*PROVIDES:\s*(\w+)\s*(.+?)\n\s*STORY_CONTEXT:\s*(.+?)(?=\n- NPC:|\nTASKS:|\n\n|$)',
            section_text,
            re.DOTALL
        )
        
        for match in npc_blocks:
            name = match.group(1).strip()
            npc_id = match.group(2).strip()
            location = match.group(3).strip()
            role = match.group(4).strip()
            personality = match.group(5).strip()
            outcome_id = match.group(6).strip()
            outcome_desc = match.group(7).strip()
            story_context = match.group(8).strip()
            
            npcs.append(NPC(
                id=npc_id,
                name=name,
                location=location,
                role=role,
                personality=personality,
                outcome_provided=outcome_id,
                story_context=story_context
            ))
        
        return npcs
    
    def _extract_tasks(self) -> List[Task]:
        """Extract all TASK entries"""
        tasks = []
        
        # Find TASKS section
        tasks_section = re.search(
            r'TASKS:(.*?)(?=\nSTORY_END|$)',
            self.story_text,
            re.DOTALL
        )
        
        if not tasks_section:
            self.errors.append("No TASKS section found")
            return tasks
        
        section_text = tasks_section.group(1)
        
        # Parse starting tasks first
        starting_section = re.search(
            r'STARTING_TASKS:(.*?)(?=\nTASK_CHAIN:|$)',
            section_text,
            re.DOTALL
        )
        
        if starting_section:
            tasks.extend(self._parse_task_block(starting_section.group(1), is_starting=True))
        
        # Parse task chain
        chain_section = re.search(
            r'TASK_CHAIN:(.*?)$',
            section_text,
            re.DOTALL
        )
        
        if chain_section:
            tasks.extend(self._parse_task_block(chain_section.group(1), is_starting=False))
        
        return tasks
    
    def _parse_task_block(self, text: str, is_starting: bool) -> List[Task]:
        """Parse a block of task definitions"""
        tasks = []
        
        # Pattern: - Task ID (role) at location: description
        #           TYPE: type
        #           ... type-specific fields ...
        #           NEEDS: prerequisites (optional)
        #           UNLOCK: tasks (optional)
        #           FINAL: true (optional)
        
        task_blocks = re.finditer(
            r'- Task\s+([A-Z]+\d+[a-z]?)\s+\(([^)]+)\)\s+at\s+(\w+):\s*(.+?)\n(.*?)(?=\n- Task|\n\n|$)',
            text,
            re.DOTALL
        )
        
        for match in task_blocks:
            task_id = match.group(1).strip()
            role = match.group(2).strip()
            location = match.group(3).strip()
            description = match.group(4).strip()
            details = match.group(5)
            
            # Extract TYPE
            type_match = re.search(r'TYPE:\s*(\w+)', details)
            if not type_match:
                self.errors.append(f"Task {task_id} missing TYPE")
                continue
            
            task_type = type_match.group(1).strip()
            
            # Create base task
            task = Task(
                id=task_id,
                role=role,
                type=task_type,
                location=location,
                description=description
            )
            
            # Extract type-specific fields
            if task_type == 'search':
                find_match = re.search(r'FIND:\s*(.+?)(?=\n|$)', details)
                if find_match:
                    items = [i.strip() for i in find_match.group(1).split(',')]
                    task.search_items = items
            
            elif task_type == 'npc_llm':
                talk_match = re.search(r'TALK_TO:\s*(\w+)', details)
                get_match = re.search(r'GET:\s*(\w+)', details)
                
                if talk_match:
                    task.npc_id = talk_match.group(1).strip()
                if get_match:
                    task.target_outcome = get_match.group(1).strip()
            
            elif task_type == 'minigame':
                # Extract minigame ID from TYPE line
                minigame_match = re.search(r'TYPE:\s*minigame\s*\(([^)]+)\)', details)
                if minigame_match:
                    task.minigame_id = minigame_match.group(1).strip()
            
            elif task_type == 'handoff':
                handoff_match = re.search(r'HANDOFF:\s*(\w+)\s+to\s+(\w+)', details)
                if handoff_match:
                    task.handoff_item = handoff_match.group(1).strip()
                    task.handoff_to_role = handoff_match.group(2).strip()
            
            elif task_type == 'info_share':
                share_match = re.search(r'SHARE:\s*(\w+)\s+with\s+(.+?)(?=\n|$)', details)
                if share_match:
                    task.info_id = share_match.group(1).strip()
                    task.share_with = share_match.group(2).strip()
            
            # Extract prerequisites (NEEDS line)
            if not is_starting:
                needs_match = re.search(r'NEEDS:\s*(.+?)(?=\n\s*(?:UNLOCK|FINAL):|$)', details, re.DOTALL)
                if needs_match:
                    needs_text = needs_match.group(1)
                    task.prerequisites = self._parse_prerequisites(needs_text)
            
            # Check if final task
            if re.search(r'FINAL:\s*true', details, re.IGNORECASE):
                task.is_final = True
            
            tasks.append(task)
        
        return tasks
    
    def _parse_prerequisites(self, prereq_text: str) -> List[Dict[str, str]]:
        """Parse prerequisite text into structured format"""
        prerequisites = []
        
        # Pattern: "item_id (from TaskID)" or "outcome_id (from TaskID)" or "TaskID (description)"
        
        # Task prerequisites: "TaskID" or "Task TaskID"
        for match in re.finditer(r'(?:Task\s+)?([A-Z]+\d+[a-z]?)\s*\(', prereq_text):
            task_id = match.group(1)
            prerequisites.append({'type': 'task', 'id': task_id})
        
        # Item prerequisites: "item_id (from ...)" or just "item_id"
        for match in re.finditer(r'(\w+)\s*\(from [A-Z]+\d+', prereq_text):
            item_id = match.group(1)
            # Check if this looks like an item (not a task ID)
            if not re.match(r'^[A-Z]+\d+', item_id):
                prerequisites.append({'type': 'item', 'id': item_id})
        
        # Outcome prerequisites: "outcome_id (from ...)"
        # Look for outcome IDs that aren't item IDs or task IDs
        for word in prereq_text.split(','):
            word = word.strip()
            # If it has underscores and doesn't look like a task ID, might be an outcome
            if '_' in word:
                # Extract ID before any parenthesis
                id_match = re.match(r'(\w+)\s*\(', word)
                if id_match:
                    potential_id = id_match.group(1)
                    # If not already added as task or item, treat as outcome
                    if not any(p['id'] == potential_id for p in prerequisites):
                        prerequisites.append({'type': 'outcome', 'id': potential_id})
        
        return prerequisites
    


def extract_structure(story_text: str, scenario_id: str, roles: List[str]) -> ScenarioGraph:
    """
    Parse story text and extract structured graph
    
    Args:
        story_text: Semi-structured story from Stage 1
        scenario_id: Scenario ID
        roles: List of role IDs
    
    Returns:
        ScenarioGraph object
    """
    parser = StoryParser(story_text)
    graph = parser.parse(scenario_id, roles)
    
    if parser.errors:
        print(f"⚠️  Parsing warnings:")
        for error in parser.errors:
            print(f"   - {error}")
    
    return graph


if __name__ == '__main__':
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Extract structure from story (Stage 2)")
    parser.add_argument("story_file", help="Path to story text file")
    parser.add_argument("--scenario", required=True, help="Scenario ID")
    parser.add_argument("--roles", nargs="+", required=True, help="Role IDs")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    print(f"📊 Extracting structure from story...")
    print(f"   Story: {args.story_file}")
    print()
    
    # Load story
    story_path = Path(args.story_file)
    if not story_path.exists():
        print(f"❌ Story file not found: {story_path}")
        sys.exit(1)
    
    story_text = story_path.read_text()
    
    # Extract structure
    graph = extract_structure(story_text, args.scenario, args.roles)
    
    # Save to JSON
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = story_path.with_suffix('.json')
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(graph.to_json())
    
    print(f"✅ Extracted structure:")
    print(f"   Locations: {len(graph.locations)}")
    print(f"   Items: {len(graph.items)}")
    print(f"   NPCs: {len(graph.npcs)}")
    print(f"   Tasks: {len(graph.tasks)}")
    print(f"💾 Saved to: {output_path}")
