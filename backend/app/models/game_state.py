"""
Data models for game state and tasks
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum


class TaskType(str, Enum):
    """Type of task"""
    MINIGAME = "minigame"        # Player-controlled action (e.g., wire_connecting)
    NPC_LLM = "npc_llm"          # Dialogue with AI-controlled NPC
    SEARCH = "search"            # Search location for items
    HANDOFF = "handoff"          # Transfer item between players
    INFO_SHARE = "info_share"    # Verbal information exchange (real-life)
    DISCOVERY = "discovery"      # Open-ended exploration task


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


class Task(BaseModel):
    """A task that a player must complete"""
    id: str = Field(..., description="Unique task ID (e.g., 'MM1', 'H3')")
    type: TaskType = Field(..., description="Type of task")
    description: str = Field(..., description="What player needs to do")
    assigned_role: str = Field(..., description="Role this task belongs to")
    assigned_player_id: Optional[str] = Field(None, description="Specific player assigned")
    location: str = Field(..., description="Where task takes place")
    status: TaskStatus = Field(default=TaskStatus.LOCKED, description="Current status")
    dependencies: List[str] = Field(default_factory=list, description="Task IDs that must complete first")
    
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
        """Check if all dependencies are met"""
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)
    
    def unlock_if_ready(self, completed_task_ids: set) -> bool:
        """Change status to AVAILABLE if dependencies met"""
        if self.status == TaskStatus.LOCKED and self.can_start(completed_task_ids):
            self.status = TaskStatus.AVAILABLE
            return True
        return False


class NPCData(BaseModel):
    """NPC information for conversations"""
    id: str = Field(..., description="NPC identifier")
    name: str = Field(..., description="NPC display name")
    role: str = Field(..., description="NPC's job/role")
    personality: str = Field(..., description="Personality description for LLM")
    location: str = Field(..., description="Where NPC is located")


class Item(BaseModel):
    """An item that can be found, carried, and used"""
    id: str = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="What the item is")
    location: Optional[str] = Field(None, description="Where item is located (None if in player inventory)")
    required_for: Optional[str] = Field(None, description="Task ID or objective this enables")
    hidden: bool = Field(default=False, description="Requires thorough search to find")
    quantity: int = Field(default=1, description="Number available")
    transferable: bool = Field(default=True, description="Can be given to other players")


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
    
    def complete_task(self, task_id: str) -> List[str]:
        """
        Mark task as completed and unlock dependent tasks
        Returns list of newly unlocked task IDs
        """
        if task_id not in self.tasks:
            return []
        
        # Mark as completed
        self.tasks[task_id].status = TaskStatus.COMPLETED
        
        # Get all completed task IDs
        completed = self.get_completed_task_ids()
        
        # Check all locked tasks to see if they can be unlocked
        newly_available = []
        for task in self.tasks.values():
            if task.unlock_if_ready(completed):
                newly_available.append(task.id)
        
        return newly_available
    
    def get_npc_by_id(self, npc_id: str) -> Optional[NPCData]:
        """Get NPC data by ID"""
        for npc in self.npcs:
            if npc.id == npc_id:
                return npc
        return None
    
    def is_game_won(self) -> bool:
        """Check if all tasks are completed"""
        return all(task.status == TaskStatus.COMPLETED for task in self.tasks.values())
