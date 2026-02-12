"""
Data models for game state and tasks
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class TaskType(str, Enum):
    """Type of task"""
    MINIGAME = "minigame"        # Player-controlled action (e.g., wire_connecting)
    NPC_LLM = "npc_llm"          # Dialogue with AI-controlled NPC
    SEARCH = "search"            # Search location for items
    HANDOFF = "handoff"          # Transfer item between players
    INFO_SHARE = "info_share"    # Verbal information exchange (real-life)


class TaskStatus(str, Enum):
    """Current status of a task"""
    LOCKED = "locked"            # Dependencies not met
    AVAILABLE = "available"      # Can be started
    IN_PROGRESS = "in_progress"  # Currently being worked on
    COMPLETED = "completed"      # Finished successfully


class Location(BaseModel):
    """A location in the game world"""
    id: str = Field(..., description="Unique location identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Location description")
    category: str = Field(..., description="Location category (e.g., 'Museum Interior')")
    visual: str = Field(default="", description="Visual description for image generation")


class PrerequisiteType(str, Enum):
    """Type of prerequisite for a task"""
    TASK = "task"            # Another task must be completed
    OUTCOME = "outcome"      # An NPC outcome (info or action) must be achieved
    ITEM = "item"            # Player must have this item in inventory


class Prerequisite(BaseModel):
    """A prerequisite that must be met before a task can start"""
    type: PrerequisiteType = Field(..., description="Type of prerequisite")
    id: str = Field(..., description="ID of the task, outcome, or item required")
    description: Optional[str] = Field(None, description="Human-readable description")


class Task(BaseModel):
    """A task that a player must complete"""
    id: str = Field(..., description="Unique task ID (e.g., 'MM1', 'H3')")
    type: TaskType = Field(..., description="Type of task")
    description: str = Field(..., description="What player needs to do")
    detail_description: str = Field(default="", description="Longer description with specifics (e.g. intel details)")
    assigned_role: str = Field(..., description="Role this task belongs to")
    assigned_player_id: Optional[str] = Field(None, description="Specific player assigned")
    location: str = Field(..., description="Where task takes place")
    status: TaskStatus = Field(default=TaskStatus.LOCKED, description="Current status")
    
    # Prerequisites (typed: task, outcome, item)
    prerequisites: List[Prerequisite] = Field(default_factory=list, description="Prerequisites to unlock this task")
    # Keep dependencies for backward compatibility during migration
    dependencies: List[str] = Field(default_factory=list, description="Task IDs that must complete first (legacy)")
    
    # NPC task completion criteria
    target_outcomes: List[str] = Field(default_factory=list, description="For NPC_LLM: outcome IDs to achieve for auto-completion")
    
    # Type-specific metadata
    minigame_id: Optional[str] = Field(None, description="For MINIGAME: which minigame to play")
    npc_id: Optional[str] = Field(None, description="For NPC_LLM: which NPC to talk to")
    npc_name: Optional[str] = Field(None, description="For NPC_LLM: NPC display name")
    npc_personality: Optional[str] = Field(None, description="For NPC_LLM: personality description")
    search_items: List[str] = Field(default_factory=list, description="For SEARCH: items to find")
    handoff_item: Optional[str] = Field(None, description="For HANDOFF: item to transfer")
    handoff_to_role: Optional[str] = Field(None, description="For HANDOFF: recipient role")
    info_description: Optional[str] = Field(None, description="For INFO_SHARE: what info to share")
    
    def can_start(self, completed_task_ids: set) -> bool:
        """Check if all dependencies are met (legacy task-ID only)"""
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)
    
    def can_start_rich(self, completed_task_ids: set, achieved_outcomes: set, player_items: set) -> bool:
        """Check if all typed prerequisites are met"""
        for prereq in self.prerequisites:
            if prereq.type == PrerequisiteType.TASK and prereq.id not in completed_task_ids:
                return False
            if prereq.type == PrerequisiteType.OUTCOME and prereq.id not in achieved_outcomes:
                return False
            if prereq.type == PrerequisiteType.ITEM and prereq.id not in player_items:
                return False
        return True
    
    def unlock_if_ready(self, completed_task_ids: set, achieved_outcomes: set = None, player_items: set = None) -> bool:
        """Change status to AVAILABLE if all prerequisites are met"""
        if self.status != TaskStatus.LOCKED:
            return False
        
        # Use rich prerequisites if available, otherwise fall back to legacy
        if self.prerequisites:
            if self.can_start_rich(
                completed_task_ids,
                achieved_outcomes or set(),
                player_items or set(),
            ):
                self.status = TaskStatus.AVAILABLE
                return True
        elif self.can_start(completed_task_ids):
            self.status = TaskStatus.AVAILABLE
            return True
        
        return False


class NPCInfoItem(BaseModel):
    """A piece of information an NPC knows"""
    info_id: Optional[str] = Field(None, description="Trackable ID (None = flavor only)")
    confidence: str = Field(..., description="How freely NPC shares: HIGH, MEDIUM, LOW")
    description: str = Field(..., description="What the NPC knows")


class NPCAction(BaseModel):
    """An action an NPC can be convinced to perform"""
    action_id: str = Field(..., description="Trackable action ID")
    confidence: str = Field(..., description="How hard to convince: HIGH, MEDIUM, LOW, VERY HIGH")
    description: str = Field(..., description="What the NPC can be convinced to do")


class NPCCoverOption(BaseModel):
    """A cover story a player can use when talking to this NPC"""
    cover_id: str = Field(..., description="Cover identifier (e.g., 'new_guard', 'journalist')")
    description: str = Field(..., description="What the player claims to be")
    npc_reaction: str = Field(default="", description="How the NPC feels about this cover (fed to LLM)")


class NPCData(BaseModel):
    """NPC information for conversations and image generation"""
    id: str = Field(..., description="NPC identifier")
    name: str = Field(..., description="NPC display name")
    role: str = Field(..., description="NPC's job/role")
    personality: str = Field(..., description="Personality description for LLM")
    location: str = Field(..., description="Where NPC is located")
    gender: str = Field(default="person", description="Gender for image generation")
    ethnicity: str = Field(default="", description="Ethnicity for image generation")
    clothing: str = Field(default="", description="Clothing description for image generation")
    expression: str = Field(default="friendly", description="Facial expression for image generation")
    attitude: str = Field(default="approachable", description="Personality vibe for image generation")
    details: str = Field(default="", description="Visual details/props for image generation")
    
    # Relationships with other NPCs (injected into LLM as background flavor)
    relationships: str = Field(default="", description="Who else this NPC knows and how they relate to them")
    
    # Story context: immutable world facts the NPC must never contradict
    story_context: str = Field(default="", description="Ground-truth facts about the world this NPC knows, preventing LLM improvisation errors")
    
    # Structured conversation data
    information_known: List[NPCInfoItem] = Field(default_factory=list, description="Info items this NPC knows")
    actions_available: List[NPCAction] = Field(default_factory=list, description="Actions this NPC can be convinced to perform")
    cover_options: List[NPCCoverOption] = Field(default_factory=list, description="Cover stories players can use with this NPC")


class Item(BaseModel):
    """An item that can be found, carried, and used"""
    id: str = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="What the item is")
    visual: str = Field(default="", description="Visual description for image generation")
    location: Optional[str] = Field(None, description="Where item is located (None if in player inventory)")
    required_for: Optional[str] = Field(None, description="Task ID or objective this enables")
    hidden: bool = Field(default=False, description="Requires thorough search to find")
    quantity: int = Field(default=1, description="Number available")
    transferable: bool = Field(default=True, description="Can be given to other players")
    unlock_prerequisites: List[Prerequisite] = Field(
        default_factory=list,
        description="Prerequisites that must be met for item to appear in search results"
    )


class GameState(BaseModel):
    """The complete state of an active game"""
    objective: str = Field(..., description="Main goal of the heist")
    scenario: str = Field(..., description="Scenario identifier")
    locations: List[Location] = Field(default_factory=list, description="All locations")
    tasks: Dict[str, Task] = Field(default_factory=dict, description="task_id -> Task")
    npcs: List[NPCData] = Field(default_factory=list, description="All NPCs in scenario")
    items_by_location: Dict[str, List[Item]] = Field(default_factory=dict, description="location_name -> available items")
    timeline_minutes: int = Field(default=120, description="Total time available")
    elapsed_minutes: int = Field(default=0, description="Time elapsed")
    
    # NPC conversation tracking
    achieved_outcomes: Dict[str, List[str]] = Field(default_factory=dict, description="player_id -> [outcome_ids] (persists across cooldowns)")
    npc_suspicion: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="player_id -> {npc_id -> suspicion_level 0-5}")
    npc_cooldowns: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="player_id -> {npc_id -> cooldown_expiry_timestamp}")
    chosen_covers: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="player_id -> {npc_id -> cover_id}")
    
    def get_tasks_for_role(self, role: str) -> List[Task]:
        """Get all tasks assigned to a specific role"""
        return [task for task in self.tasks.values() if task.assigned_role == role]
    
    def get_available_tasks_for_role(self, role: str) -> List[Task]:
        """Get tasks that are currently available for a role"""
        return [
            task for task in self.tasks.values()
            if task.assigned_role == role and task.status == TaskStatus.AVAILABLE
        ]
    
    def get_completed_task_ids(self) -> set:
        """Get set of all completed task IDs"""
        return {task.id for task in self.tasks.values() if task.status == TaskStatus.COMPLETED}
    
    def complete_task(self, task_id: str, player_id: str = None, room=None) -> List[str]:
        """
        Mark task as completed and unlock dependent tasks.
        Uses rich prerequisites (TASK, OUTCOME, ITEM) when available.
        Returns list of newly unlocked task IDs.
        """
        if task_id not in self.tasks:
            return []
        
        # Mark as completed
        self.tasks[task_id].status = TaskStatus.COMPLETED
        
        return self._check_unlocks(player_id, room=room)
    
    def _check_unlocks(self, player_id: str = None, room=None) -> List[str]:
        """Re-check all locked tasks and unlock any whose prerequisites are now met.
        
        If room is provided, checks each task against its assigned player's inventory.
        Otherwise item prerequisites are deferred to check_unlocks_with_items().
        """
        completed = self.get_completed_task_ids()
        
        # Gather all achieved outcomes (across all players)
        all_outcomes: set = set()
        for outcomes in self.achieved_outcomes.values():
            all_outcomes.update(outcomes)
        
        # Build a role -> player_items mapping if room is available
        role_items: dict = {}
        if room:
            for pid, p in room.players.items():
                role_items[p.role] = {item.id for item in p.inventory}
        
        newly_available = []
        for task in self.tasks.values():
            # Use the assigned player's items for item prerequisites
            task_player_items = role_items.get(task.assigned_role, set()) if room else set()
            if task.unlock_if_ready(completed, all_outcomes, task_player_items):
                newly_available.append(task.id)
        
        return newly_available
    
    def check_unlocks_with_items(self, player_items: set) -> List[str]:
        """Re-check locked tasks considering a specific player's inventory."""
        completed = self.get_completed_task_ids()
        
        all_outcomes: set = set()
        for outcomes in self.achieved_outcomes.values():
            all_outcomes.update(outcomes)
        
        newly_available = []
        for task in self.tasks.values():
            if task.unlock_if_ready(completed, all_outcomes, player_items):
                newly_available.append(task.id)
        
        return newly_available
    
    def check_item_visible(self, item: 'Item') -> bool:
        """Check if an item's unlock prerequisites are met (visible in search results).
        
        Uses the same prerequisite types as tasks: Task, Outcome, Item.
        Items with no unlock_prerequisites are always visible.
        """
        if not item.unlock_prerequisites:
            return True
        
        completed = self.get_completed_task_ids()
        
        all_outcomes: set = set()
        for outcomes in self.achieved_outcomes.values():
            all_outcomes.update(outcomes)
        
        for prereq in item.unlock_prerequisites:
            if prereq.type == PrerequisiteType.TASK and prereq.id not in completed:
                return False
            if prereq.type == PrerequisiteType.OUTCOME and prereq.id not in all_outcomes:
                return False
            # For item prerequisites, check if ANY player has the item
            # (unlike tasks which check assigned player's inventory)
            if prereq.type == PrerequisiteType.ITEM:
                # Item prereqs on items are rare but supported
                # We can't easily check inventory here without room reference
                # so we skip for now -- task prereqs and outcomes cover the main cases
                pass
        
        return True
    
    def get_npc_by_id(self, npc_id: str) -> Optional[NPCData]:
        """Get NPC data by ID"""
        for npc in self.npcs:
            if npc.id == npc_id:
                return npc
        return None
    
    def is_game_won(self) -> bool:
        """Check if all tasks are completed"""
        return all(task.status == TaskStatus.COMPLETED for task in self.tasks.values())
