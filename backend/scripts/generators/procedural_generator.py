"""
Procedural Graph Generator
Generates valid scenario graphs using deterministic algorithms.
Structure (tasks, prerequisites, unlock chains) is procedural.
Names and descriptions are enriched with a single LLM call at the end.
"""

import json
import logging
import random
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    MINIGAME = "minigame"
    NPC_LLM = "npc_llm"
    SEARCH = "search"
    HANDOFF = "handoff"
    INFO_SHARE = "info_share"


class PrerequisiteType(str, Enum):
    TASK = "task"
    OUTCOME = "outcome"
    ITEM = "item"


@dataclass
class Prerequisite:
    type: str  # "task", "outcome", "item"
    id: str
    description: Optional[str] = None


@dataclass
class Location:
    id: str
    name: str
    description: str
    category: str
    visual: str = ""


@dataclass
class Item:
    id: str
    name: str
    description: str
    location: str
    hidden: bool = False
    unlock_prerequisites: List[Prerequisite] = field(default_factory=list)
    visual: str = ""
    required_for: Optional[str] = None
    quantity: int = 1
    transferable: bool = True


@dataclass
class NPCInfoItem:
    info_id: Optional[str]
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    description: str


@dataclass
class NPCAction:
    action_id: str
    confidence: str  # "HIGH", "MEDIUM", "LOW", "VERY HIGH"
    description: str


@dataclass
class NPCCoverOption:
    cover_id: str
    description: str
    npc_reaction: str = ""


@dataclass
class NPC:
    id: str
    name: str
    role: str
    personality: str
    location: str
    information_known: List[NPCInfoItem] = field(default_factory=list)
    actions_available: List[NPCAction] = field(default_factory=list)
    cover_options: List[NPCCoverOption] = field(default_factory=list)
    gender: str = "person"
    ethnicity: str = ""
    clothing: str = ""
    expression: str = "neutral"
    attitude: str = "professional"
    details: str = ""
    relationships: str = ""
    story_context: str = ""


@dataclass
class Task:
    id: str
    type: str  # TaskType
    description: str
    assigned_role: str
    location: str
    prerequisites: List[Prerequisite] = field(default_factory=list)
    status: str = "locked"
    detail_description: str = ""
    
    # Type-specific fields
    minigame_id: Optional[str] = None
    npc_id: Optional[str] = None
    npc_name: Optional[str] = None
    npc_personality: Optional[str] = None
    target_outcomes: List[str] = field(default_factory=list)
    search_items: List[str] = field(default_factory=list)
    handoff_item: Optional[str] = None
    handoff_to_role: Optional[str] = None
    info_description: Optional[str] = None


@dataclass
class ScenarioGraph:
    scenario_id: str
    objective: str
    locations: List[Location]
    items: List[Item]
    npcs: List[NPC]
    tasks: List[Task]
    timeline_minutes: int = 120


@dataclass
class GeneratorConfig:
    """Configuration for procedural generation"""
    location_count: Tuple[int, int] = (4, 8)
    items_per_location: Tuple[int, int] = (1, 3)
    npc_count: Tuple[int, int] = (2, 4)
    tasks_per_role: Tuple[int, int] = (3, 6)
    hidden_item_ratio: float = 0.3
    task_type_distribution: Dict[str, float] = field(default_factory=lambda: {
        "minigame": 0.40,
        "npc_llm": 0.35,
        "search": 0.25,
        "handoff": 0.00,  # Disabled: requires complex item prerequisite chains
        "info_share": 0.00,  # Disabled: requires outcome tracking complexity
    })
    timeline_minutes: int = 120
    seed: Optional[int] = None


# Role code mapping (must match shared_data/roles.json and experience_loader.py)
ROLE_CODES = {
    "mastermind": "MM", "hacker": "H", "safe_cracker": "SC", "insider": "I",
    "driver": "D", "grifter": "G", "muscle": "M", "lookout": "L",
    "fence": "F", "cat_burglar": "CB", "cleaner": "CL", "pickpocket": "PP",
}

# Available minigames
MINIGAMES = [
    "wire_connecting",
    "lock_picking",
    "fingerprint_matching",
    "safe_cracking",
    "camera_bypass",
    "alarm_disable",
]


class ProceduralGraphGenerator:
    """Generates valid scenario graphs using deterministic algorithms"""
    
    def __init__(self, config: GeneratorConfig = None):
        self.config = config or GeneratorConfig()
        if self.config.seed is not None:
            random.seed(self.config.seed)
    
    def generate(self, scenario_id: str, role_ids: List[str]) -> ScenarioGraph:
        """Generate a complete scenario graph"""
        
        # 1. Generate locations (zones: start → middle → end)
        locations = self._generate_locations(scenario_id)
        
        # 2. Generate items with unlock chains
        items = self._generate_items(locations)
        
        # 3. Generate NPCs with outcomes
        npcs = self._generate_npcs(locations)
        
        # 4. Generate task graph (the critical part)
        tasks = self._generate_task_graph(role_ids, locations, items, npcs)
        
        # 5. Create objective
        objective = self._generate_objective(scenario_id)
        
        graph = ScenarioGraph(
            scenario_id=scenario_id,
            objective=objective,
            locations=locations,
            items=items,
            npcs=npcs,
            tasks=tasks,
            timeline_minutes=self.config.timeline_minutes
        )
        
        # 6. Enrich names/descriptions with a single LLM call
        _enrich_graph_with_llm(graph, role_ids)
        
        return graph
    
    def _generate_locations(self, scenario_id: str) -> List[Location]:
        """Generate locations in logical zones"""
        location_count = random.randint(*self.config.location_count)
        
        # Common location patterns based on scenario type
        if "museum" in scenario_id:
            location_templates = [
                ("entrance_hall", "Entrance Hall", "Museum Interior", "Grand entrance with security"),
                ("exhibit_floor", "Exhibit Floor", "Museum Interior", "Main gallery with displays"),
                ("storage_room", "Storage Room", "Museum Interior", "Back storage area"),
                ("security_office", "Security Office", "Museum Interior", "Security monitoring room"),
                ("vault_chamber", "Vault Chamber", "Museum Interior", "Secure vault room"),
                ("rooftop", "Rooftop Access", "Museum Exterior", "Rooftop entrance point"),
                ("loading_dock", "Loading Dock", "Museum Exterior", "Service entrance"),
            ]
        elif "bank" in scenario_id:
            location_templates = [
                ("lobby", "Bank Lobby", "Bank Interior", "Main customer area"),
                ("teller_area", "Teller Area", "Bank Interior", "Transaction stations"),
                ("manager_office", "Manager Office", "Bank Interior", "Bank manager workspace"),
                ("server_room", "Server Room", "Bank Interior", "IT infrastructure"),
                ("vault", "Vault", "Bank Interior", "Main vault"),
                ("parking_garage", "Parking Garage", "Bank Exterior", "Underground parking"),
            ]
        elif "office" in scenario_id:
            location_templates = [
                ("reception", "Reception Area", "Office Interior", "Front desk"),
                ("cubicle_farm", "Cubicle Farm", "Office Interior", "Open workspace"),
                ("executive_suite", "Executive Suite", "Office Interior", "C-level offices"),
                ("server_room", "Server Room", "Office Interior", "Data center"),
                ("archive_room", "Archive Room", "Office Interior", "Document storage"),
                ("rooftop", "Rooftop", "Office Exterior", "Roof access"),
            ]
        else:
            # Generic heist locations
            location_templates = [
                ("entry_point", "Entry Point", "Exterior", "Initial access point"),
                ("main_area", "Main Area", "Interior", "Primary area"),
                ("secure_area", "Secure Area", "Interior", "Restricted zone"),
                ("target_room", "Target Room", "Interior", "Final objective room"),
            ]
        
        # Select random subset
        selected = random.sample(
            location_templates, 
            min(location_count, len(location_templates))
        )
        
        locations = []
        for loc_id, name, category, desc in selected:
            locations.append(Location(
                id=loc_id,
                name=name,
                description=desc,
                category=category,
                visual=f"{name.lower()} environment"
            ))
        
        return locations
    
    def _generate_items(self, locations: List[Location]) -> List[Item]:
        """Generate items with logical unlock chains"""
        items = []
        item_counter = 1
        
        for location in locations:
            item_count = random.randint(*self.config.items_per_location)
            
            for _ in range(item_count):
                item_id = f"item_{item_counter}"
                is_hidden = random.random() < self.config.hidden_item_ratio
                
                items.append(Item(
                    id=item_id,
                    name=f"Item {item_counter}",
                    description=f"A useful item found at {location.name}",
                    location=location.id,
                    hidden=is_hidden,
                    unlock_prerequisites=[],  # Will be filled in task generation
                    visual=f"generic item {item_counter}"
                ))
                item_counter += 1
        
        return items
    
    def _generate_npcs(self, locations: List[Location]) -> List[NPC]:
        """Generate NPCs with outcomes (information and actions)"""
        npc_count = random.randint(*self.config.npc_count)
        
        # Common NPC archetypes
        npc_templates = [
            ("security_guard", "Security Guard", "guard", "Cautious and rule-following"),
            ("janitor", "Janitor", "maintenance", "Friendly but observant"),
            ("curator", "Curator", "curator", "Knowledgeable and proud"),
            ("receptionist", "Receptionist", "receptionist", "Professional and helpful"),
            ("it_specialist", "IT Specialist", "IT", "Technical and distracted"),
            ("manager", "Manager", "manager", "Busy and authoritative"),
        ]
        
        selected_npc_templates = random.sample(
            npc_templates,
            min(npc_count, len(npc_templates))
        )
        
        npcs = []
        for i, (npc_id, name, role, personality) in enumerate(selected_npc_templates):
            # Assign to random location
            location = random.choice(locations)
            
            # Each NPC has 1-2 information items and 1-2 actions
            info_count = random.randint(1, 2)
            action_count = random.randint(1, 2)
            
            information_known = []
            for j in range(info_count):
                info_id = f"{npc_id}_info_{j+1}"
                information_known.append(NPCInfoItem(
                    info_id=info_id,
                    confidence=random.choice(["HIGH", "MEDIUM", "LOW"]),
                    description=f"Information from {name}"
                ))
            
            actions_available = []
            for j in range(action_count):
                action_id = f"{npc_id}_action_{j+1}"
                actions_available.append(NPCAction(
                    action_id=action_id,
                    confidence=random.choice(["HIGH", "MEDIUM", "LOW"]),
                    description=f"Action performed by {name}"
                ))
            
            # Generate cover options
            cover_options = [
                NPCCoverOption(
                    cover_id="direct",
                    description="Be direct and honest",
                    npc_reaction="Suspicious but may help if convinced"
                ),
                NPCCoverOption(
                    cover_id="lie",
                    description="Use a false cover story",
                    npc_reaction="May believe or may see through it"
                ),
            ]
            
            npcs.append(NPC(
                id=npc_id,
                name=name,
                role=role,
                personality=personality,
                location=location.id,
                information_known=information_known,
                actions_available=actions_available,
                cover_options=cover_options,
                gender=random.choice(["man", "woman", "person"]),
                expression=random.choice(["neutral", "friendly", "stern"]),
                attitude=random.choice(["professional", "casual", "suspicious"]),
            ))
        
        return npcs
    
    def _generate_task_graph(
        self,
        role_ids: List[str],
        locations: List[Location],
        items: List[Item],
        npcs: List[NPC]
    ) -> List[Task]:
        """
        Generate a valid task dependency graph.
        
        Algorithm:
        1. Create starting tasks for each role (no prerequisites)
        2. Create chains of tasks with dependencies
        3. Ensure all tasks are reachable from starting tasks
        4. Add cross-role dependencies (handoffs, info shares)
        5. Link hidden items to task unlocks
        """
        tasks = []
        task_counters = {role: 1 for role in role_ids}
        
        # Track available prerequisite sources
        # Note: For starting tasks, we don't use prerequisites
        # For dependent tasks, we only reference already-created tasks
        available_task_ids: Set[str] = set()
        available_outcomes: Set[str] = set()
        available_items: Set[str] = set()
        
        # Get all NPC outcomes (these exist from the start)
        npc_outcomes = self._get_all_npc_outcomes(npcs)
        
        # Build items_by_location mapping (ALL items - hidden and non-hidden)
        items_by_location = {}
        items_by_id = {item.id: item for item in items}
        for item in items:
            if item.location not in items_by_location:
                items_by_location[item.location] = []
            items_by_location[item.location].append(item.id)
        
        assigned_items: Set[str] = set()
        
        for role in role_ids:
            role_code = ROLE_CODES.get(role, role[:2].upper())
            tasks_for_role = random.randint(*self.config.tasks_per_role)
            
            for task_num in range(1, tasks_for_role + 1):
                task_id = f"{role_code}{task_num}"
                
                # First task for each role is a starting task
                if task_num == 1:
                    task = self._create_starting_task(
                        task_id, role, locations
                    )
                else:
                    # Create task with dependencies on previous tasks
                    task = self._create_dependent_task(
                        task_id,
                        role,
                        role_ids,
                        locations,
                        items,
                        npcs,
                        available_task_ids,
                        available_outcomes,
                        available_items
                    )
                
                # If it's a search task, populate items (ensuring no duplicates)
                if task.type == TaskType.SEARCH.value:
                    location_items = items_by_location.get(task.location, [])
                    available_location_items = [
                        item_id for item_id in location_items
                        if item_id not in assigned_items
                    ]
                    # Starting search tasks (no prerequisites) can only use non-hidden items
                    # - no "earlier" tasks exist to unlock hidden items
                    if not task.prerequisites:
                        available_location_items = [
                            item_id for item_id in available_location_items
                            if not items_by_id[item_id].hidden
                        ]
                    
                    if available_location_items:
                        num_items = min(random.randint(1, 2), len(available_location_items))
                        selected_items = random.sample(available_location_items, num_items)
                        task.search_items = selected_items
                        assigned_items.update(selected_items)
                    else:
                        # No items available - convert to minigame instead
                        task.type = TaskType.MINIGAME.value
                        task.minigame_id = random.choice(MINIGAMES)
                        task.description = f"Complete {task.minigame_id.replace('_', ' ')}"
                        task.search_items = []
                
                tasks.append(task)
                available_task_ids.add(task_id)
                
                # If this is an NPC task, add its outcomes as available
                if task.type == TaskType.NPC_LLM.value and task.target_outcomes:
                    available_outcomes.update(task.target_outcomes)
                
                # If this is a search task, add its items as available
                if task.type == TaskType.SEARCH.value and task.search_items:
                    available_items.update(task.search_items)
        
        # Link hidden items to task prerequisites (avoid circular: unlock tasks must not include search task for this item)
        self._link_hidden_items_to_tasks(items, tasks)
        
        return tasks
    
    def _create_starting_task(
        self,
        task_id: str,
        role: str,
        locations: List[Location]
    ) -> Task:
        """Create a starting task (no prerequisites)"""
        
        # Starting tasks are usually minigames or searches
        task_type = random.choice([TaskType.MINIGAME, TaskType.SEARCH])
        location = random.choice(locations)
        
        if task_type == TaskType.MINIGAME:
            minigame = random.choice(MINIGAMES)
            return Task(
                id=task_id,
                type=task_type.value,
                description=f"Complete {minigame.replace('_', ' ')}",
                assigned_role=role,
                location=location.id,
                prerequisites=[],
                status="locked",
                minigame_id=minigame
            )
        else:  # SEARCH
            return Task(
                id=task_id,
                type=task_type.value,
                description=f"Search for items at {location.name}",
                assigned_role=role,
                location=location.id,
                prerequisites=[],
                status="locked",
                search_items=[]  # Will be populated after items are generated
            )
    
    def _create_dependent_task(
        self,
        task_id: str,
        role: str,
        role_ids: List[str],
        locations: List[Location],
        items: List[Item],
        npcs: List[NPC],
        available_task_ids: Set[str],
        available_outcomes: Set[str],
        available_items: Set[str]
    ) -> Task:
        """Create a task with dependencies"""
        
        # Choose task type based on distribution
        task_type = self._weighted_choice(self.config.task_type_distribution)
        location = random.choice(locations)
        
        # Create prerequisites (1-3 prerequisites from available sources)
        prerequisites = self._create_prerequisites(
            available_task_ids,
            available_outcomes,
            available_items,
            min_prereqs=1,
            max_prereqs=2
        )
        
        if task_type == "minigame":
            minigame = random.choice(MINIGAMES)
            return Task(
                id=task_id,
                type=task_type,
                description=f"Complete {minigame.replace('_', ' ')}",
                assigned_role=role,
                location=location.id,
                prerequisites=prerequisites,
                minigame_id=minigame
            )
        
        elif task_type == "npc_llm":
            # Pick a random NPC
            if npcs:
                npc = random.choice(npcs)
                # Target 1-2 outcomes from this NPC
                npc_all_outcomes = [item.info_id for item in npc.information_known if item.info_id] + \
                                   [action.action_id for action in npc.actions_available]
                
                target_outcomes = random.sample(
                    npc_all_outcomes,
                    min(random.randint(1, 2), len(npc_all_outcomes))
                ) if npc_all_outcomes else []
                
                return Task(
                    id=task_id,
                    type=task_type,
                    description=f"Talk to {npc.name}",
                    assigned_role=role,
                    location=npc.location,
                    prerequisites=prerequisites,
                    npc_id=npc.id,
                    npc_name=npc.name,
                    npc_personality=npc.personality,
                    target_outcomes=target_outcomes
                )
            else:
                # No NPCs available, fall back to search
                task_type = "search"
        
        if task_type == "search":
            # Note: search_items will be empty here
            # They will be populated later by inline logic during task generation
            return Task(
                id=task_id,
                type=task_type,
                description=f"Search {location.name}",
                assigned_role=role,
                location=location.id,
                prerequisites=prerequisites,
                search_items=[]  # Populated during task generation
            )
        
        elif task_type == "handoff":
            # Pick another role to hand off to
            other_roles = [r for r in role_ids if r != role]
            if other_roles and available_items:
                target_role = random.choice(other_roles)
                handoff_item = random.choice(list(available_items))
                
                return Task(
                    id=task_id,
                    type=task_type,
                    description=f"Hand off item to {target_role}",
                    assigned_role=role,
                    location=location.id,
                    prerequisites=prerequisites,
                    handoff_item=handoff_item,
                    handoff_to_role=target_role
                )
            else:
                # Can't create handoff, fall back to minigame
                task_type = "minigame"
                return Task(
                    id=task_id,
                    type=task_type,
                    description=f"Complete {random.choice(MINIGAMES).replace('_', ' ')}",
                    assigned_role=role,
                    location=location.id,
                    prerequisites=prerequisites,
                    minigame_id=random.choice(MINIGAMES)
                )
        
        elif task_type == "info_share":
            # Verbal information share (requires prior knowledge)
            if available_outcomes:
                outcome_id = random.choice(list(available_outcomes))
                
                return Task(
                    id=task_id,
                    type=task_type,
                    description=f"Share information with team",
                    assigned_role=role,
                    location=location.id,
                    prerequisites=prerequisites,
                    info_description=f"Information about {outcome_id}"
                )
            else:
                # No info to share yet, fall back to minigame
                task_type = "minigame"
                return Task(
                    id=task_id,
                    type=task_type,
                    description=f"Complete {random.choice(MINIGAMES).replace('_', ' ')}",
                    assigned_role=role,
                    location=location.id,
                    prerequisites=prerequisites,
                    minigame_id=random.choice(MINIGAMES)
                )
        
        # Default fallback
        return Task(
            id=task_id,
            type=TaskType.MINIGAME.value,
            description="Complete task",
            assigned_role=role,
            location=location.id,
            prerequisites=prerequisites,
            minigame_id=random.choice(MINIGAMES)
        )
    
    def _create_prerequisites(
        self,
        available_task_ids: Set[str],
        available_outcomes: Set[str],
        available_items: Set[str],
        min_prereqs: int = 1,
        max_prereqs: int = 2
    ) -> List[Prerequisite]:
        """Create a list of prerequisites from available sources"""
        
        prereq_count = random.randint(min_prereqs, max_prereqs)
        prerequisites = []
        
        # Build pool of available prerequisites
        # For now, only use task and outcome prerequisites (not item prerequisites)
        # This avoids complex item-reachability issues
        prereq_pool = []
        
        for task_id in available_task_ids:
            prereq_pool.append(("task", task_id))
        
        for outcome_id in available_outcomes:
            prereq_pool.append(("outcome", outcome_id))
        
        # Note: Skipping item prerequisites for simplicity
        # Items are accessed via search tasks, which have task prerequisites
        
        if not prereq_pool:
            return []
        
        # Sample prerequisites
        selected = random.sample(
            prereq_pool,
            min(prereq_count, len(prereq_pool))
        )
        
        for prereq_type, prereq_id in selected:
            prerequisites.append(Prerequisite(
                type=prereq_type,
                id=prereq_id,
                description=None
            ))
        
        return prerequisites
    
    def _link_hidden_items_to_tasks(self, items: List[Item], tasks: List[Task]) -> None:
        """Ensure hidden items have unlock prerequisites without circular dependencies.
        
        A hidden item's unlock_prerequisites must NOT include the search task that
        looks for it (would create circular: task needs item, item needs task).
        """
        # Build map: item_id -> set of task_ids that search for this item
        tasks_searching_for_item: Dict[str, Set[str]] = {}
        for task in tasks:
            if task.type == TaskType.SEARCH.value:
                for item_id in task.search_items:
                    if item_id not in tasks_searching_for_item:
                        tasks_searching_for_item[item_id] = set()
                    tasks_searching_for_item[item_id].add(task.id)
        
        all_task_ids = {t.id for t in tasks}
        
        for item in items:
            if item.hidden and not item.unlock_prerequisites:
                # Forbidden: tasks that search for this item (would create circular dependency)
                forbidden_tasks = tasks_searching_for_item.get(item.id, set())
                valid_tasks = list(all_task_ids - forbidden_tasks)
                
                if not valid_tasks:
                    # Cannot create valid chain - make item visible instead
                    item.hidden = False
                    continue
                
                prereq_count = random.randint(1, min(2, len(valid_tasks)))
                selected_tasks = random.sample(valid_tasks, prereq_count)
                
                for task_id in selected_tasks:
                    item.unlock_prerequisites.append(Prerequisite(
                        type="task",
                        id=task_id,
                        description=None
                    ))
    
    def _get_all_npc_outcomes(self, npcs: List[NPC]) -> List[str]:
        """Get all outcome IDs from all NPCs"""
        outcomes = []
        for npc in npcs:
            for info in npc.information_known:
                if info.info_id:
                    outcomes.append(info.info_id)
            for action in npc.actions_available:
                outcomes.append(action.action_id)
        return outcomes
    
    def _populate_search_tasks(self, tasks: List[Task], items: List[Item]) -> None:
        """Populate search tasks with items from their locations"""
        
        # Build location -> items mapping
        items_by_location = {}
        for item in items:
            if item.location not in items_by_location:
                items_by_location[item.location] = []
            items_by_location[item.location].append(item.id)
        
        # Track which items have been assigned
        assigned_items: Set[str] = set()
        
        # Populate search tasks
        for task in tasks:
            if task.type == TaskType.SEARCH.value:
                location_items = items_by_location.get(task.location, [])
                # Only use items that haven't been assigned to another task
                available_items = [item_id for item_id in location_items if item_id not in assigned_items]
                
                if available_items:
                    # Assign 1-2 items from this location
                    num_items = min(random.randint(1, 2), len(available_items))
                    selected_items = random.sample(available_items, num_items)
                    task.search_items = selected_items
                    assigned_items.update(selected_items)
    
    def _weighted_choice(self, distribution: Dict[str, float]) -> str:
        """Choose a random item based on weighted distribution"""
        items = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(items, weights=weights, k=1)[0]
    
    def _generate_objective(self, scenario_id: str) -> str:
        """Generate objective based on scenario type"""
        if "museum" in scenario_id:
            return "Steal the priceless artifact from the museum vault"
        elif "bank" in scenario_id:
            return "Infiltrate the bank and access the vault"
        elif "office" in scenario_id:
            return "Steal confidential documents from the executive suite"
        else:
            return "Complete the heist successfully"


def _enrich_graph_with_llm(graph: ScenarioGraph, role_ids: List[str]) -> None:
    """
    Replace placeholder item/NPC/task names with scenario-specific ones via a single LLM call.
    Mutates the graph in-place. Silently falls back to placeholders if the call fails.
    """
    try:
        from config import GEMINI_API_KEY, GEMINI_EXPERIENCE_MODEL
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=GEMINI_EXPERIENCE_MODEL,
            generation_config={"temperature": 0.8, "response_mime_type": "application/json"}
        )
    except Exception as e:
        logger.warning(f"LLM enrichment skipped (import failed): {e}")
        return

    scenario_id = graph.scenario_id
    location_names = {loc.id: loc.name for loc in graph.locations}
    roles_str = ", ".join(role_ids)

    # Build compact context for the LLM
    items_ctx = [
        {"id": item.id, "location": location_names.get(item.location, item.location), "hidden": item.hidden}
        for item in graph.items
    ]
    npcs_ctx = [
        {"id": npc.id, "role": npc.role, "location": location_names.get(npc.location, npc.location)}
        for npc in graph.npcs
    ]
    tasks_ctx = [
        {"id": t.id, "type": t.type, "role": t.assigned_role, "location": location_names.get(t.location, t.location)}
        for t in graph.tasks
    ]

    prompt = f"""You are a heist game writer. Given the structure below, write compelling names and descriptions.

SCENARIO: {scenario_id.replace("_", " ")}
ROLES: {roles_str}
LOCATIONS: {", ".join(location_names.values())}

ITEMS (give each a name, short description, and visual description for image generation):
{json.dumps(items_ctx, indent=2)}

NPCS (give each a first name appropriate to their role and location):
{json.dumps(npcs_ctx, indent=2)}

TASKS (give each a short action-oriented description, 5-8 words):
{json.dumps(tasks_ctx, indent=2)}

Return ONLY this JSON (no markdown):
{{
  "items": [{{"id": "item_1", "name": "...", "description": "...", "visual": "..."}}],
  "npcs": [{{"id": "security_guard", "name": "..."}}],
  "tasks": [{{"id": "MM1", "description": "..."}}]
}}"""

    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text)

        # Apply item enrichment (keep IDs, only update display fields)
        item_map = {i["id"]: i for i in data.get("items", [])}
        for item in graph.items:
            if item.id in item_map:
                enriched = item_map[item.id]
                item.name = enriched.get("name", item.name)
                item.description = enriched.get("description", item.description)
                item.visual = enriched.get("visual", item.visual)

        # Apply NPC name enrichment
        npc_map = {n["id"]: n for n in data.get("npcs", [])}
        for npc in graph.npcs:
            if npc.id in npc_map:
                npc.name = npc_map[npc.id].get("name", npc.name)

        # Apply task description enrichment
        task_map = {t["id"]: t for t in data.get("tasks", [])}
        for task in graph.tasks:
            if task.id in task_map:
                task.description = task_map[task.id].get("description", task.description)

        logger.info(f"[enrichment] Enriched {len(item_map)} items, {len(npc_map)} NPCs, {len(task_map)} tasks")

    except Exception as e:
        logger.warning(f"[enrichment] LLM enrichment failed, keeping placeholders: {e}")


def generate_scenario_graph(
    scenario_id: str,
    role_ids: List[str],
    config: GeneratorConfig = None
) -> ScenarioGraph:
    """Main entry point for procedural graph generation"""
    
    generator = ProceduralGraphGenerator(config)
    graph = generator.generate(scenario_id, role_ids)
    
    return graph
