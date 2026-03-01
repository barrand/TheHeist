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
from pathlib import Path
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
    age: int = 35
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
        "minigame": 0.30,
        "npc_llm": 0.30,
        "search": 0.20,
        "handoff": 0.10,
        "info_share": 0.10,
    })
    timeline_minutes: int = 120
    seed: Optional[int] = None


# Role code mapping (must match shared_data/roles.json and experience_loader.py)
ROLE_CODES = {
    "mastermind": "MM", "hacker": "H", "safe_cracker": "SC", "insider": "I",
    "driver": "D", "grifter": "G", "muscle": "M", "lookout": "L",
    "fence": "F", "cat_burglar": "CB", "cleaner": "CL", "pickpocket": "PP",
}

def _load_role_minigames() -> Dict[str, List[str]]:
    """Load per-role minigame lists from shared_data/roles.json.

    Returns a dict mapping role_id -> [minigame_id, ...].
    Also stores a '_all' key with every valid minigame ID across all roles,
    used as a last-resort fallback in _pick_minigame.
    """
    try:
        roles_path = Path(__file__).parent.parent.parent.parent / "shared_data" / "roles.json"
        with open(roles_path) as f:
            data = json.load(f)
        role_map = {
            role["role_id"]: [mg["id"] for mg in role.get("minigames", [])]
            for role in data.get("roles", [])
        }
        # Derive a global fallback from the union of all per-role minigames.
        # This guarantees the fallback only contains IDs that exist in roles.json.
        all_valid = list({mg for ids in role_map.values() for mg in ids})
        role_map["_all"] = all_valid
        return role_map
    except Exception as e:
        logger.warning(f"[minigames] Could not load roles.json: {e}")
        # Absolute last resort — wire_connecting exists for hacker and is broadly safe
        return {"_all": ["wire_connecting"]}


class ProceduralGraphGenerator:
    """Generates valid scenario graphs using deterministic algorithms"""
    
    def __init__(self, config: GeneratorConfig = None):
        self.config = config or GeneratorConfig()
        if self.config.seed is not None:
            random.seed(self.config.seed)
        self._role_minigames: Dict[str, List[str]] = _load_role_minigames()

    def _pick_minigame(self, role: str) -> str:
        """Return a valid minigame ID for the given role.

        Uses the role-specific list from roles.json. Falls back to the union
        of all valid minigame IDs (_all) if the role has no specific list.
        Never uses hardcoded IDs that aren't in roles.json.
        """
        role_mgs = self._role_minigames.get(role, [])
        if role_mgs:
            return random.choice(role_mgs)
        # Role not found or no minigames — use union of all valid IDs
        all_mgs = self._role_minigames.get("_all", ["wire_connecting"])
        return random.choice(all_mgs)

    def _role_can_do_minigame(self, role: str) -> bool:
        """Return False for roles (like Mastermind) that have no minigames in roles.json."""
        role_mgs = self._role_minigames.get(role)
        # If roles.json was loaded and the role explicitly has an empty list, no minigames
        if role_mgs is not None and len(role_mgs) == 0:
            return False
        return True
    
    def generate(self, scenario_id: str, role_ids: List[str], progress_fn=None) -> ScenarioGraph:
        """Generate a complete scenario graph"""
        _p = progress_fn or (lambda msg: None)  # no-op if no callback provided

        # 1. LLM generates the creative setting: locations, objective, and NPC placement.
        _p(f"Generating setting with LLM (locations, objective, NPC placement)...")
        llm_setting = _generate_setting_with_llm(scenario_id, role_ids, self.config)

        # 2. Use LLM locations if available, else fall back to templates
        if llm_setting and llm_setting.get("locations"):
            locations = [
                Location(
                    id=loc["id"],
                    name=loc["name"],
                    description=loc["description"],
                    category=loc.get("category", "Interior"),
                    visual=loc.get("visual", loc["name"].lower()),
                )
                for loc in llm_setting["locations"]
            ]
            objective = llm_setting.get("objective") or self._generate_objective(scenario_id)
            _p(f"Setting generated: {len(locations)} locations — {objective[:80]}")
        else:
            locations = self._generate_locations_fallback(scenario_id)
            objective = self._generate_objective(scenario_id)
            _p(f"Setting generated (fallback): {len(locations)} locations")

        # npc_placement maps archetype_id -> location_id (from LLM, may be None/empty)
        npc_placement = llm_setting.get("npc_placement", {}) if llm_setting else {}

        # 3. Generate items with unlock chains
        _p(f"Building items, NPCs, and task graph...")
        items = self._generate_items(locations)
        
        # 4. Generate NPCs with contextual placement
        npcs = self._generate_npcs(locations, npc_placement)
        
        # 5. Generate task graph (the critical part)
        tasks = self._generate_task_graph(role_ids, locations, items, npcs)

        task_type_counts = {}
        for t in tasks:
            task_type_counts[t.type] = task_type_counts.get(t.type, 0) + 1
        breakdown = ", ".join(f"{v}×{k}" for k, v in sorted(task_type_counts.items()))
        _p(f"Task graph built: {len(tasks)} tasks ({breakdown}), {len(npcs)} NPCs, {len(items)} items")

        graph = ScenarioGraph(
            scenario_id=scenario_id,
            objective=objective,
            locations=locations,
            items=items,
            npcs=npcs,
            tasks=tasks,
            timeline_minutes=self.config.timeline_minutes
        )

        # 6. Pre-enrichment structural validation.
        #    Fix cycles/orphans NOW on the cheap raw graph so we never waste expensive
        #    LLM enrichment calls on a structurally broken graph.
        raw_cycles = _detect_cycles_raw(graph.tasks)
        if raw_cycles:
            _p(f"  Raw graph has {len(raw_cycles)} cycle(s) — aborting before enrichment")
            raise ValueError(f"Raw graph has unresolvable cycles: {raw_cycles}")

        # 7. Enrich item/NPC/task names and full NPC profiles via LLM.
        #    This rewrites NPC info IDs (placeholder → real LLM names) and updates
        #    task target_outcomes to match.
        _enrich_graph_with_llm(graph, role_ids, progress_fn=progress_fn)

        # 8. Post-enrichment graph guarantees — run AFTER enrichment so these use
        #    the real LLM-generated outcome IDs, not placeholder stubs.
        if len(role_ids) > 1:
            self._ensure_cross_role_chain(graph.tasks)
        self._ensure_minimum_cross_role_tasks(graph.tasks, role_ids, graph.items)

        # 8b. Post-enrichment structural check — the cross-role wiring in step 8 can
        #     introduce new edges. Abort now rather than wasting export + validation.
        post_cycles = _detect_cycles_raw(graph.tasks)
        if post_cycles:
            _p(f"  Post-enrichment cross-role wiring introduced {len(post_cycles)} cycle(s) — aborting")
            raise ValueError(f"Post-enrichment cycles: {post_cycles}")

        return graph
    
    def _generate_locations_fallback(self, scenario_id: str) -> List[Location]:
        """Generic fallback locations used only when LLM generation fails."""
        location_count = random.randint(*self.config.location_count)
        templates = [
            ("entry_point", "Entry Point", "Exterior", "Initial access point"),
            ("main_area", "Main Area", "Interior", "Primary operational area"),
            ("secure_area", "Secure Area", "Interior", "Restricted access zone"),
            ("control_room", "Control Room", "Interior", "Security and systems hub"),
            ("target_room", "Target Room", "Interior", "Final objective location"),
        ]
        selected = random.sample(templates, min(location_count, len(templates)))
        return [
            Location(id=loc_id, name=name, description=desc, category=cat,
                     visual=f"{name.lower()} environment")
            for loc_id, name, cat, desc in selected
        ]
    
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
    
    def _generate_npcs(self, locations: List[Location], npc_placement: Dict[str, str] = None) -> List[NPC]:
        """Generate NPCs with outcomes (information and actions).

        npc_placement maps archetype_id -> location_id from the LLM setting call.
        Falls back to random.choice when an archetype has no placement or the dict is empty.
        """
        npc_placement = npc_placement or {}
        npc_count = random.randint(*self.config.npc_count)
        location_id_set = {loc.id for loc in locations}
        location_by_id = {loc.id: loc for loc in locations}
        
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
            # Use LLM-suggested placement if valid, else fall back to random
            suggested_loc_id = npc_placement.get(npc_id)
            if suggested_loc_id and suggested_loc_id in location_id_set:
                location = location_by_id[suggested_loc_id]
            else:
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
        available_task_ids: Set[str] = set()

        # Pre-seed with all NPC outcomes — NPCs are present from game start, so any role
        # can reference their outcomes as "info to share" without waiting for tasks to run.
        npc_outcomes = self._get_all_npc_outcomes(npcs)
        available_outcomes: Set[str] = set(npc_outcomes)

        # Pre-seed with all non-hidden items — visible items exist in locations from the
        # start, so handoff tasks can reference them before a search task has run.
        available_items: Set[str] = {item.id for item in items if not item.hidden}
        
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
            prev_task_id: Optional[str] = None  # tracks the preceding task for this role
            
            for task_num in range(1, tasks_for_role + 1):
                task_id = f"{role_code}{task_num}"
                
                # First task for each role is a starting task
                if task_num == 1:
                    task = self._create_starting_task(
                        task_id, role, locations, npcs
                    )
                else:
                    # Create task with dependencies on previous tasks.
                    # prev_task_id is passed so the dependent task ALWAYS chains
                    # from its immediate predecessor, preventing dead-end tasks.
                    task = self._create_dependent_task(
                        task_id,
                        role,
                        role_ids,
                        locations,
                        items,
                        npcs,
                        available_task_ids,
                        available_outcomes,
                        available_items,
                        prev_task_id=prev_task_id,
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
                        # No items available - convert to minigame or npc_llm for no-minigame roles
                        if self._role_can_do_minigame(task.assigned_role):
                            mg = self._pick_minigame(task.assigned_role)
                            task.type = TaskType.MINIGAME.value
                            task.minigame_id = mg
                            task.description = f"Complete {mg.replace('_', ' ')}"
                        else:
                            task.type = TaskType.NPC_LLM.value
                            task.description = "Gather information from a contact"
                        task.search_items = []
                
                tasks.append(task)
                available_task_ids.add(task_id)
                prev_task_id = task_id  # track for next iteration's mandatory prereq
                
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
        locations: List[Location],
        npcs: List[NPC] = None
    ) -> Task:
        """Create a starting task (no prerequisites)"""
        location = random.choice(locations)

        # Roles with no minigames (e.g. Mastermind) start with an NPC or search task
        if not self._role_can_do_minigame(role):
            if npcs:
                npc = random.choice(npcs)
                npc_outcomes = [i.info_id for i in npc.information_known if i.info_id]
                target_outcomes = [random.choice(npc_outcomes)] if npc_outcomes else []
                return Task(
                    id=task_id,
                    type=TaskType.NPC_LLM.value,
                    description=f"Talk to {npc.name}",
                    assigned_role=role,
                    location=npc.location,
                    prerequisites=[],
                    status="locked",
                    npc_id=npc.id,
                    npc_name=npc.name,
                    npc_personality=npc.personality,
                    target_outcomes=target_outcomes,
                )
            # Fallback to search if no NPCs yet
            return Task(
                id=task_id,
                type=TaskType.SEARCH.value,
                description=f"Search for items at {location.name}",
                assigned_role=role,
                location=location.id,
                prerequisites=[],
                status="locked",
                search_items=[],
            )

        # Starting tasks are usually minigames or searches
        task_type = random.choice([TaskType.MINIGAME, TaskType.SEARCH])

        if task_type == TaskType.MINIGAME:
            minigame = self._pick_minigame(role)
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
        available_items: Set[str],
        prev_task_id: Optional[str] = None,
    ) -> Task:
        """Create a task with dependencies"""
        
        # Choose task type based on distribution.
        # If the role can't do minigames, redistribute minigame weight across the
        # other types proportionally rather than dumping everything into npc_llm.
        if not self._role_can_do_minigame(role):
            dist = {k: v for k, v in self.config.task_type_distribution.items() if k != "minigame"}
            total = sum(dist.values()) or 1.0
            dist = {k: v / total for k, v in dist.items()}
            task_type = self._weighted_choice(dist)
        else:
            task_type = self._weighted_choice(self.config.task_type_distribution)
        location = random.choice(locations)
        
        # Build prerequisites. Always chain from the immediate predecessor for this
        # role (prevents dead-end tasks). Optionally add one outcome prereq on top.
        if prev_task_id:
            prerequisites = [Prerequisite(type="task", id=prev_task_id)]
            # 40% chance to also require one outcome, giving the graph more richness
            if available_outcomes and random.random() < 0.4:
                oid = random.choice(list(available_outcomes))
                prerequisites.append(Prerequisite(type="outcome", id=oid))
        else:
            prerequisites = self._create_prerequisites(
                available_task_ids,
                available_outcomes,
                available_items,
                min_prereqs=1,
                max_prereqs=2
            )
        
        if task_type == "minigame":
            minigame = self._pick_minigame(role)
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
                # Prefer non-hidden items at THIS task's location so the player can
                # actually find the item before handing it off. Fall back to the
                # global non-hidden pool only if no local items are available.
                items_at_location = [
                    item.id for item in items
                    if item.location == location.id and not item.hidden
                    and item.id in available_items
                ]
                handoff_pool = items_at_location if items_at_location else list(available_items)
                handoff_item = random.choice(handoff_pool)

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
                # Can't create handoff, fall back to role-appropriate task
                if self._role_can_do_minigame(role):
                    mg = self._pick_minigame(role)
                    return Task(
                        id=task_id,
                        type="minigame",
                        description=f"Complete {mg.replace('_', ' ')}",
                        assigned_role=role,
                        location=location.id,
                        prerequisites=prerequisites,
                        minigame_id=mg
                    )
                return Task(
                    id=task_id, type="search",
                    description=f"Search {location.name}",
                    assigned_role=role, location=location.id,
                    prerequisites=prerequisites, search_items=[],
                )
        
        elif task_type == "info_share":
            # Verbal information share (requires prior knowledge)
            if available_outcomes:
                outcome_id = random.choice(list(available_outcomes))
                # Add the outcome as an explicit Outcome prerequisite so the validator
                # can trace the cross-role info chain (Rule 39)
                outcome_prereq = Prerequisite(type="outcome", id=outcome_id)
                prereqs_with_outcome = prerequisites + [outcome_prereq] if outcome_id not in [p.id for p in prerequisites] else prerequisites
                return Task(
                    id=task_id,
                    type=task_type,
                    description=f"Share information with team",
                    assigned_role=role,
                    location=location.id,
                    prerequisites=prereqs_with_outcome,
                    info_description=f"Information about {outcome_id}"
                )
            else:
                # No info to share yet, fall back to role-appropriate task
                if self._role_can_do_minigame(role):
                    mg = self._pick_minigame(role)
                    return Task(
                        id=task_id,
                        type="minigame",
                        description=f"Complete {mg.replace('_', ' ')}",
                        assigned_role=role,
                        location=location.id,
                        prerequisites=prerequisites,
                        minigame_id=mg
                    )
                return Task(
                    id=task_id, type="search",
                    description=f"Search {location.name}",
                    assigned_role=role, location=location.id,
                    prerequisites=prerequisites, search_items=[],
                )
        
        # Default fallback — use role-appropriate task
        if self._role_can_do_minigame(role):
            mg = self._pick_minigame(role)
            return Task(
                id=task_id,
                type=TaskType.MINIGAME.value,
                description=f"Complete {mg.replace('_', ' ')}",
                assigned_role=role,
                location=location.id,
                prerequisites=prerequisites,
                minigame_id=mg
            )
        return Task(
            id=task_id, type="search",
            description=f"Search {location.name}",
            assigned_role=role, location=location.id,
            prerequisites=prerequisites, search_items=[],
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
    
    def _ensure_minimum_cross_role_tasks(self, tasks: List[Task], role_ids: List[str], items: List = None) -> None:
        """Guarantee at least MIN_HANDOFF handoff and MIN_INFO_SHARE info_share tasks exist.

        Candidate pool includes minigame, search, AND npc_llm dependent tasks so this
        works even when all tasks are npc_llm (e.g. Mastermind-heavy scenarios).
        Minimums match the validator's Rule 17 thresholds exactly.
        """
        MIN_HANDOFF = 3   # matches validator Rule 17 minimum
        MIN_INFO_SHARE = 2

        handoff_count = sum(1 for t in tasks if t.type == TaskType.HANDOFF.value)
        info_share_count = sum(1 for t in tasks if t.type == TaskType.INFO_SHARE.value)

        # Collect all real outcome IDs from NPC tasks (after enrichment these are real names)
        available_outcomes = []
        for t in tasks:
            if t.type == TaskType.NPC_LLM.value:
                available_outcomes.extend(t.target_outcomes)

        # Build per-role ordered task lists so we can determine which search tasks
        # PRECEDE a given handoff task. A role can only hand off items they have
        # already picked up — items from search tasks that come AFTER the handoff
        # in the chain are not yet in the player's inventory.
        items_by_id: Dict[str, "Item"] = {item.id: item for item in (items or [])}
        role_task_order: Dict[str, List[str]] = {}
        for t in tasks:
            role_task_order.setdefault(t.assigned_role, []).append(t.id)
        for role_key in role_task_order:
            role_code = ROLE_CODES.get(role_key, role_key[:2].upper())
            role_task_order[role_key].sort(
                key=lambda tid: int(tid[len(role_code):]) if tid[len(role_code):].isdigit() else 0
            )

        def _items_available_before(role: str, task_id: str) -> List[str]:
            """Return non-hidden item IDs role R will have acquired before reaching task_id.

            Only includes items from search tasks that appear earlier in the role's
            ordered task chain. Hidden items are excluded — they require prerequisites
            and can't be reliably pre-acquired for a handoff.
            """
            ordered = role_task_order.get(role, [])
            try:
                cutoff = ordered.index(task_id)
            except ValueError:
                return []
            result = []
            for earlier_id in ordered[:cutoff]:
                for t2 in tasks:
                    if t2.id == earlier_id and t2.type == TaskType.SEARCH.value:
                        for item_id in (t2.search_items or []):
                            item_obj = items_by_id.get(item_id)
                            if item_obj and not item_obj.hidden:
                                result.append(item_id)
            return result

        items_in_any_search: Set[str] = {
            item_id
            for t in tasks
            if t.type == TaskType.SEARCH.value
            for item_id in (t.search_items or [])
        }

        # Items already claimed by a handoff task (from the initial graph build)
        items_in_handoffs: Set[str] = {
            t.handoff_item for t in tasks
            if t.type == TaskType.HANDOFF.value and t.handoff_item
        }

        # Global pool of non-hidden, unclaimed items as a fallback
        all_non_hidden = [
            item.id for item in (items or [])
            if not item.hidden
            and item.id not in items_in_any_search
            and item.id not in items_in_handoffs
        ]

        # Candidates: dependent tasks (have prerequisites), not escape tasks.
        # Include npc_llm so we can always find candidates even in mastermind-heavy scenarios.
        candidates = [
            t for t in tasks
            if t.prerequisites
            and t.type in (TaskType.MINIGAME.value, TaskType.SEARCH.value, TaskType.NPC_LLM.value)
            and not getattr(t, "_is_escape", False)
        ]

        # Shuffle to vary which tasks get converted across runs
        random.shuffle(candidates)
        idx = 0

        while handoff_count < MIN_HANDOFF and idx < len(candidates):
            t = candidates[idx]
            role = t.assigned_role
            other_roles = [r for r in role_ids if r != role]
            if not other_roles:
                idx += 1
                continue

            # Items in OTHER roles' search tasks — grabbing these would cause a conflict
            # because the other role will pick up the item first, leaving none for us.
            other_role_search_items: Set[str] = {
                item_id
                for t2 in tasks
                if t2.assigned_role != role and t2.type == TaskType.SEARCH.value
                for item_id in (t2.search_items or [])
            }

            # Only use items the role has already picked up BEFORE reaching this task
            # AND that no other role's search task will also claim.
            role_pool = [
                item_id for item_id in _items_available_before(role, t.id)
                if item_id not in items_in_handoffs
                and item_id not in other_role_search_items
            ]
            # Fallback: non-hidden items at this task's location that aren't in any search
            if not role_pool:
                location_items = [
                    item.id for item in (items or [])
                    if item.location == t.location and not item.hidden
                    and item.id not in items_in_any_search
                    and item.id not in items_in_handoffs
                ]
                role_pool = location_items

            chosen_item = None
            if role_pool:
                chosen_item = random.choice(role_pool)
            elif all_non_hidden:
                chosen_item = random.choice(all_non_hidden)
                all_non_hidden.remove(chosen_item)

            if not chosen_item:
                logger.info(f"[cross-role] No acquirable item for {role} handoff — skipping {t.id}")
                idx += 1
                continue

            items_in_handoffs.add(chosen_item)

            t.type = TaskType.HANDOFF.value
            t.handoff_to_role = random.choice(other_roles)
            t.handoff_item = chosen_item
            t.npc_id = None
            t.npc_name = None
            t.minigame_id = None
            t.target_outcomes = []
            t.description = f"Hand off to {t.handoff_to_role.replace('_', ' ')}"
            handoff_count += 1
            candidates.pop(idx)
            logger.info(f"[cross-role] Converted {t.id} ({role}) to handoff → {t.handoff_to_role} (item: {t.handoff_item})")

        while info_share_count < MIN_INFO_SHARE and idx < len(candidates):
            if available_outcomes:
                t = candidates[idx]
                oid = random.choice(available_outcomes)
                # For npc_llm → info_share: keep the prerequisite chain, clear NPC fields
                t.type = TaskType.INFO_SHARE.value
                t.info_description = f"Information about {oid}"
                t.npc_id = None
                t.npc_name = None
                t.minigame_id = None
                t.target_outcomes = []
                t.description = "Share intelligence with the team"
                # Ensure the outcome is an explicit prerequisite for Rule 39 tracing
                if oid not in [p.id for p in t.prerequisites]:
                    t.prerequisites.append(Prerequisite(type="outcome", id=oid))
                info_share_count += 1
                candidates.pop(idx)
                logger.info(f"[cross-role] Converted {t.id} ({t.assigned_role}) to info_share (outcome: {oid})")
            else:
                idx += 1

    def _ensure_cross_role_chain(self, tasks: List[Task]) -> None:
        """Guarantee at least one outcome flows from one role's NPC task to a different role's prerequisite.

        If no such chain exists after generation, inject one by adding an Outcome prerequisite
        to the first eligible dependent task of a different role. This ensures Rule 39 passes.
        """
        # Map: outcome_id -> set of roles that learned it via NPC_LLM target_outcomes
        outcome_learned_by: Dict[str, Set[str]] = {}
        for t in tasks:
            if t.type == TaskType.NPC_LLM.value:
                for oid in t.target_outcomes:
                    outcome_learned_by.setdefault(oid, set()).add(t.assigned_role)

        if not outcome_learned_by:
            return  # No NPC outcomes exist — nothing to chain

        # Map: outcome_id -> set of roles that already require it as a prerequisite
        outcome_required_by: Dict[str, Set[str]] = {}
        for t in tasks:
            for prereq in t.prerequisites:
                if prereq.type == "outcome":
                    outcome_required_by.setdefault(prereq.id, set()).add(t.assigned_role)

        # Check if a cross-role chain already exists
        for oid, learning_roles in outcome_learned_by.items():
            requiring_roles = outcome_required_by.get(oid, set())
            for lr in learning_roles:
                for rr in requiring_roles:
                    if lr != rr:
                        return  # Chain already exists — nothing to do

        # No chain found — inject one. Pick the first outcome and find a dependent
        # task for a different role to add it to.
        for oid, learning_roles in outcome_learned_by.items():
            for learning_role in learning_roles:
                # Find a dependent task (has prerequisites) assigned to a DIFFERENT role
                candidates = [
                    t for t in tasks
                    if t.assigned_role != learning_role
                    and t.prerequisites
                    and t.type not in (TaskType.HANDOFF.value, TaskType.INFO_SHARE.value)
                    and oid not in [p.id for p in t.prerequisites]
                ]
                if candidates:
                    target = candidates[0]
                    target.prerequisites.append(
                        Prerequisite(type="outcome", id=oid,
                                     description=f"Received intel from {learning_role}")
                    )
                    logger.info(
                        f"[cross-role] Injected Outcome `{oid}` (from {learning_role}) "
                        f"as prerequisite on {target.id} ({target.assigned_role})"
                    )
                    return  # One chain is enough

    def _append_escape_tasks(
        self,
        tasks: List[Task],
        role_ids: List[str],
        locations: List[Location],
    ) -> List[Task]:
        """Append a final escape task per role after the main graph is complete.

        Each escape task:
        - Prerequisites: the last task in that role's existing chain
        - Location: the first location (entry point becomes the exit)
        - Type: search (all roles can do this; enrichment rewrites it as extraction)
        - Marked with _is_escape=True so the enrichment prompt uses extraction narrative
        """
        exit_location = locations[0].id if locations else "any"
        tasks_by_role: Dict[str, List[Task]] = {}
        for t in tasks:
            tasks_by_role.setdefault(t.assigned_role, []).append(t)

        escape_tasks = []
        for role in role_ids:
            role_code = ROLE_CODES.get(role, role[:2].upper())
            role_tasks = tasks_by_role.get(role, [])
            # Find the last task in the role's chain (highest task number)
            if role_tasks:
                last_task = max(role_tasks, key=lambda t: t.id)
                prereq = [Prerequisite(type="task", id=last_task.id)]
                escape_task_id = f"{role_code}{len(role_tasks) + 1}"
            else:
                prereq = []
                escape_task_id = f"{role_code}1"

            escape_task = Task(
                id=escape_task_id,
                type=TaskType.SEARCH.value,
                description=f"Escape with the crew",
                assigned_role=role,
                location=exit_location,
                prerequisites=prereq,
                status="locked",
                search_items=[],
            )
            # Tag for enrichment prompt to write extraction narrative
            object.__setattr__(escape_task, "_is_escape", True) if False else None
            escape_task.__dict__["_is_escape"] = True
            escape_tasks.append(escape_task)

        return tasks + escape_tasks

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
        elif "mansion" in scenario_id:
            return "Break into the panic room and retrieve the hidden assets"
        elif "casino" in scenario_id:
            return "Crack the casino vault and walk out with the chips"
        elif "train" in scenario_id:
            return "Board the armored train and steal the guarded cargo"
        elif "lab" in scenario_id or "research" in scenario_id:
            return "Extract the prototype from the secure research facility"
        elif "art" in scenario_id or "gallery" in scenario_id:
            return "Swap the famous painting with a convincing forgery"
        elif "police" in scenario_id or "evidence" in scenario_id:
            return "Recover the evidence from the police station before it's processed"
        elif "prison" in scenario_id or "detention" in scenario_id:
            return "Extract the target from custody without triggering a lockdown"
        elif "dock" in scenario_id or "ship" in scenario_id or "port" in scenario_id:
            return "Locate and retrieve the cargo from the guarded shipping yard"
        else:
            return "Complete the heist successfully"


def _generate_setting_with_llm(
    scenario_id: str,
    role_ids: List[str],
    config: "GeneratorConfig",
) -> Optional[Dict]:
    """
    Ask the LLM to invent the physical setting for this heist: locations, objective,
    and contextual NPC placement.

    Returns a dict with 'locations', 'objective', and 'npc_placement', or None on failure.
    Locations and NPC placement are creative and specific to this scenario run.
    """
    try:
        from config import GEMINI_API_KEY, GEMINI_EXPERIENCE_MODEL
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=GEMINI_EXPERIENCE_MODEL,
            generation_config={"temperature": 1.0, "response_mime_type": "application/json"}
        )
    except Exception as e:
        logger.warning(f"[setting] LLM unavailable, using fallback locations: {e}")
        return None

    location_count = random.randint(*config.location_count)
    roles_str = ", ".join(role_ids)
    scenario_name = scenario_id.replace("_", " ")

    # Fixed NPC archetypes that the generator always uses
    npc_archetypes = [
        "security_guard", "janitor", "curator",
        "receptionist", "it_specialist", "manager"
    ]
    npc_archetypes_str = ", ".join(npc_archetypes)

    prompt = f"""You are a creative heist game designer. Invent a vivid, specific setting for this heist.

SCENARIO: {scenario_name}
ROLES: {roles_str}
NUMBER OF LOCATIONS: {location_count}

Design {location_count} distinct locations the players will move through — from entry point to final objective.
Make them creative, atmospheric, and specific to the scenario (not generic). Each location should feel like
a real place with character. IDs must be snake_case, unique, and concise.

Also write a single compelling objective sentence (what the crew is trying to accomplish).

Finally, for each NPC archetype below, assign the most contextually appropriate location ID from your list.
Place people where they would realistically work: a security_guard at an entrance or checkpoint, a janitor
in maintenance or back corridors, a curator near the exhibit or vault, a manager in an office, etc.

NPC archetypes to place: {npc_archetypes_str}

Return ONLY this JSON:
{{
  "objective": "One punchy sentence describing the heist goal",
  "locations": [
    {{
      "id": "snake_case_id",
      "name": "Display Name",
      "category": "Interior or Exterior label",
      "description": "One atmospheric sentence describing the space",
      "visual": "Short visual prompt for image generation (10-15 words)"
    }}
  ],
  "npc_placement": {{
    "security_guard": "location_id_from_above",
    "janitor": "location_id_from_above",
    "curator": "location_id_from_above",
    "receptionist": "location_id_from_above",
    "it_specialist": "location_id_from_above",
    "manager": "location_id_from_above"
  }}
}}"""

    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text)
        locs = data.get("locations", [])
        if not locs:
            return None
        logger.info(
            f"[setting] LLM generated {len(locs)} locations for {scenario_id} "
            f"with {len(data.get('npc_placement', {}))} NPC placements"
        )
        return data
    except Exception as e:
        logger.warning(f"[setting] LLM setting generation failed, using fallback: {e}")
        return None


def _clean_llm_json(text: str) -> str:
    """Strip markdown code fences and fix common LLM JSON syntax issues."""
    import re as _re
    text = text.strip()
    # Strip ```json ... ``` or ``` ... ``` fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])  # drop opening fence line
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3].rstrip()
    # Remove trailing commas before } or ] (most common LLM mistake)
    text = _re.sub(r',(\s*[}\]])', r'\1', text)
    return text.strip()


def _detect_cycles_raw(tasks: List["Task"]) -> List[str]:
    """Return a list of cycle descriptions found in the raw task prerequisite graph.

    Uses DFS with a colour-marking algorithm (white/grey/black). Only follows
    task-type prerequisites (not item/outcome edges which can't form cycles).
    Called BEFORE LLM enrichment so cycles are caught on the cheap raw graph.
    """
    task_map = {t.id: t for t in tasks}
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {tid: WHITE for tid in task_map}
    cycles: List[str] = []

    def dfs(node_id: str, path: List[str]) -> None:
        colour[node_id] = GREY
        path.append(node_id)
        task = task_map.get(node_id)
        if task:
            for prereq in task.prerequisites:
                if prereq.type != "task" or prereq.id not in task_map:
                    continue
                if colour[prereq.id] == GREY:
                    # Found a back-edge → cycle
                    cycle_start = path.index(prereq.id)
                    cycle_path = " -> ".join(path[cycle_start:] + [prereq.id])
                    cycles.append(cycle_path)
                elif colour[prereq.id] == WHITE:
                    dfs(prereq.id, path)
        path.pop()
        colour[node_id] = BLACK

    for tid in list(task_map):
        if colour[tid] == WHITE:
            dfs(tid, [])

    return cycles


def _enrich_graph_with_llm(graph: ScenarioGraph, role_ids: List[str], progress_fn=None) -> None:
    """
    Replace placeholder names/descriptions with scenario-specific content via two LLM calls:
      1. Items + tasks (fast, compact)
      2. Full NPC profiles (personality, relationships, information_known with named IDs,
         actions_available with named IDs, 3 cover story options each)
    Mutates the graph in-place. Silently falls back to placeholders if a call fails.
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

    _p = progress_fn or (lambda msg: None)

    scenario_id = graph.scenario_id
    scenario_name = scenario_id.replace("_", " ")
    location_names = {loc.id: loc.name for loc in graph.locations}
    roles_str = ", ".join(role_ids)
    locations_str = ", ".join(location_names.values())

    # --- Call 1: Items + tasks ---
    items_ctx = [
        {"id": item.id, "location": location_names.get(item.location, item.location), "hidden": item.hidden}
        for item in graph.items
    ]
    tasks_ctx = [
        {"id": t.id, "type": t.type, "role": t.assigned_role, "location": location_names.get(t.location, t.location),
         "npc_id": t.npc_id, "is_escape": getattr(t, "_is_escape", False)}
        for t in graph.tasks
    ]

    items_tasks_prompt = f"""You are a heist game writer. Given the structure below, write compelling names and descriptions.

SCENARIO: {scenario_name}
ROLES: {roles_str}
LOCATIONS: {locations_str}

ITEMS (give each a name, short description, and a visual description for image generation):
{json.dumps(items_ctx, indent=2)}

TASKS (give each a short action-oriented description, 8-15 words; escape tasks should read as extraction/getaway narrative):
{json.dumps(tasks_ctx, indent=2)}

Return ONLY this JSON (no markdown):
{{
  "items": [{{"id": "item_1", "name": "...", "description": "...", "visual": "..."}}],
  "tasks": [{{"id": "MM1", "description": "..."}}]
}}"""

    _p(f"Enriching items and task descriptions via LLM ({len(graph.items)} items, {len(graph.tasks)} tasks)...")
    try:
        response = model.generate_content(items_tasks_prompt)
        data = json.loads(_clean_llm_json(response.text))

        item_map = {i["id"]: i for i in data.get("items", [])}
        for item in graph.items:
            if item.id in item_map:
                enriched = item_map[item.id]
                item.name = enriched.get("name", item.name)
                item.description = enriched.get("description", item.description)
                item.visual = enriched.get("visual", item.visual)

        task_map = {t["id"]: t for t in data.get("tasks", [])}
        for task in graph.tasks:
            if task.id in task_map:
                task.description = task_map[task.id].get("description", task.description)

        logger.info(f"[enrichment] Enriched {len(item_map)} items, {len(task_map)} tasks")
        _p(f"Items and tasks enriched: {len(item_map)} items named, {len(task_map)} task descriptions written")
    except Exception as e:
        logger.warning(f"[enrichment] Items/tasks LLM call failed: {e}")
        _p(f"Warning: items/tasks enrichment failed ({e}), using placeholders")

    # --- Call 2: Full NPC profiles ---
    # Build per-NPC task context so the LLM knows what each NPC needs to provide
    npc_task_ctx: Dict[str, List[str]] = {}
    for t in graph.tasks:
        if t.type == "npc_llm" and t.npc_id:
            npc_task_ctx.setdefault(t.npc_id, []).append(
                f"{t.id} ({t.assigned_role}): {t.description}"
            )
    # NPC roster summary for cross-references in relationships
    npc_roster = [
        {"id": n.id, "role": n.role, "location": location_names.get(n.location, n.location)}
        for n in graph.npcs
    ]
    npcs_ctx = [
        {
            "id": npc.id,
            "role": npc.role,
            "location": location_names.get(npc.location, npc.location),
            "tasks_targeting_this_npc": npc_task_ctx.get(npc.id, []),
        }
        for npc in graph.npcs
    ]

    npc_prompt = f"""You are a heist game character writer. Create rich, grounded NPC profiles for this scenario.

SCENARIO: {scenario_name}
SETTING OBJECTIVE: {graph.objective}
PLAYER ROLES: {roles_str}
ALL LOCATIONS: {locations_str}
ALL NPCS (for cross-references): {json.dumps(npc_roster)}

For each NPC below, write a complete profile. The NPC must feel like a real person embedded in this specific scenario.

RULES:
- `personality`: 2-3 sentences. Grounded in their job, location, and emotional state right now.
- `relationships`: 1-2 sentences cross-referencing other NPCs by name. How do they know each other?
- `story_context`: 1 sentence. What is their role in tonight's events?
- `information_known`: Real, specific facts this NPC knows about the heist target. Each must have a
  named snake_case `id` that tasks can reference as a target outcome or prerequisite.
  Include 1-3 HIGH/MEDIUM/LOW items. Make the descriptions concrete (names, locations, times, codes).
- `actions_available`: What can players convince this NPC to DO? Each has a named snake_case `id`
  players unlock by talking to them. 0-2 items. If none, return empty array.
- `cover_options`: Exactly 3 player cover identities. Each has a `cover_id`, a one-sentence cover
  identity the player uses, and an `npc_reaction` note on how the NPC behaves differently.

NPCS TO PROFILE:
{json.dumps(npcs_ctx, indent=2)}

Return ONLY this JSON (no markdown):
{{
  "npcs": [
    {{
      "id": "security_guard",
      "name": "First Last",
      "gender": "male|female|person",
      "ethnicity": "...",
      "age": 45,
      "clothing": "...",
      "expression": "...",
      "attitude": "...",
      "details": "Small physical detail (prop, accessory, posture)",
      "personality": "...",
      "relationships": "...",
      "story_context": "...",
      "information_known": [
        {{"id": "snake_case_outcome_id", "confidence": "HIGH", "description": "Specific fact..."}}
      ],
      "actions_available": [
        {{"id": "snake_case_action_id", "confidence": "HIGH", "description": "What they do when convinced..."}}
      ],
      "cover_options": [
        {{"cover_id": "label", "description": "Player's cover identity sentence", "npc_reaction": "How NPC responds"}}
      ]
    }}
  ]
}}"""

    def _try_parse_npc_response(raw_text: str) -> Optional[Dict]:
        """Try to parse NPC profile response, cleaning common LLM JSON issues."""
        try:
            return json.loads(_clean_llm_json(raw_text))
        except json.JSONDecodeError:
            return None

    npc_names = [npc.id for npc in graph.npcs]
    _p(f"Building full NPC profiles via LLM ({len(npc_names)} NPCs: {', '.join(npc_names)})...")

    data = None
    for attempt in range(2):
        try:
            if attempt > 0:
                _p(f"  Retrying NPC profile call (attempt {attempt+1}/2)...")
            response = model.generate_content(npc_prompt)
            data = _try_parse_npc_response(response.text)
            if data:
                break
            logger.warning(f"[enrichment] NPC JSON parse failed (attempt {attempt+1}/2), retrying...")
        except Exception as e:
            logger.warning(f"[enrichment] NPC LLM call error (attempt {attempt+1}/2): {e}")

    if not data:
        logger.warning(f"[enrichment] NPC profile call failed after 2 attempts, keeping placeholders")
        _p(f"Warning: NPC profile enrichment failed after 2 attempts, using placeholders")
        return

    try:
        npc_map = {n["id"]: n for n in data.get("npcs", [])}
        for npc in graph.npcs:
            enriched = npc_map.get(npc.id)
            if not enriched:
                continue

            npc.name = enriched.get("name", npc.name)
            npc.gender = enriched.get("gender", npc.gender)
            npc.ethnicity = enriched.get("ethnicity", npc.ethnicity)
            npc.age = int(enriched.get("age", npc.age))
            npc.clothing = enriched.get("clothing", npc.clothing)
            npc.expression = enriched.get("expression", npc.expression)
            npc.attitude = enriched.get("attitude", npc.attitude)
            npc.details = enriched.get("details", npc.details)
            npc.personality = enriched.get("personality", npc.personality)
            npc.relationships = enriched.get("relationships", npc.relationships)
            npc.story_context = enriched.get("story_context", npc.story_context)

            npc.information_known = [
                NPCInfoItem(
                    info_id=info.get("id"),
                    confidence=info.get("confidence", "MEDIUM"),
                    description=info.get("description", ""),
                )
                for info in enriched.get("information_known", [])
            ]
            npc.actions_available = [
                NPCAction(
                    action_id=action.get("id", "action"),
                    confidence=action.get("confidence", "MEDIUM"),
                    description=action.get("description", ""),
                )
                for action in enriched.get("actions_available", [])
            ]
            npc.cover_options = [
                NPCCoverOption(
                    cover_id=cover.get("cover_id", f"cover_{i}"),
                    description=cover.get("description", ""),
                    npc_reaction=cover.get("npc_reaction", ""),
                )
                for i, cover in enumerate(enriched.get("cover_options", []))
            ]

            # Re-wire all npc_llm tasks that target this NPC to use the enriched real
            # outcome IDs. The tasks were created with placeholder IDs like
            # `security_guard_info_1`; enrichment replaces those with LLM-generated
            # names like `vault_location`. Always overwrite so the two stay in sync.
            if npc.information_known:
                real_ids = [i.info_id for i in npc.information_known if i.info_id]
                real_ids += [a.action_id for a in npc.actions_available if a.action_id]
                if real_ids:
                    for task in graph.tasks:
                        if task.type == "npc_llm" and task.npc_id == npc.id:
                            # Keep up to 2 outcomes; prefer info IDs over action IDs
                            task.target_outcomes = real_ids[:min(2, len(real_ids))]

        logger.info(f"[enrichment] Enriched {len(npc_map)} NPCs with full profiles")
        enriched_names = [npc.name for npc in graph.npcs if npc.name != npc.id]
        _p(f"NPC profiles complete: {', '.join(enriched_names) if enriched_names else f'{len(npc_map)} NPCs enriched'}")
    except Exception as e:
        logger.warning(f"[enrichment] NPC profile application failed: {e}")
        _p(f"Warning: NPC profile application failed ({e})")


def generate_scenario_graph(
    scenario_id: str,
    role_ids: List[str],
    config: GeneratorConfig = None,
    progress_fn: Optional[callable] = None,
) -> ScenarioGraph:
    """Main entry point for procedural graph generation.

    Args:
        progress_fn: Optional callable(msg: str) invoked at each major step.
                     Useful for streaming progress to a UI during long LLM calls.
    """
    generator = ProceduralGraphGenerator(config)
    graph = generator.generate(scenario_id, role_ids, progress_fn=progress_fn)
    return graph
