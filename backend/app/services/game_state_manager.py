"""
Game State Manager Service
Manages game state, task dependencies, and state updates for active games
"""

import logging
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime

from app.models.game_state import GameState, Task, TaskStatus, TaskType
from app.models.room import GameRoom, Item

logger = logging.getLogger(__name__)


class GameStateManager:
    """
    Manages game state for all active games
    
    Responsibilities:
    - Store game state per room
    - Validate task completion attempts
    - Resolve dependencies (unlock dependent tasks)
    - Check win/loss conditions
    - Handle item transfers between players
    - Track game progress
    """
    
    def __init__(self):
        """Initialize game state manager"""
        # room_code -> GameState
        self.game_states: Dict[str, GameState] = {}
        logger.info("GameStateManager initialized")
    
    def set_game_state(self, room_code: str, game_state: GameState) -> None:
        """
        Store game state for a room
        
        Args:
            room_code: Room code
            game_state: GameState to store
        """
        self.game_states[room_code] = game_state
        logger.info(f"🎮 Game state set for room {room_code}: {len(game_state.tasks)} tasks")
    
    def get_game_state(self, room_code: str) -> Optional[GameState]:
        """Get game state for a room"""
        return self.game_states.get(room_code)
    
    def can_complete_task(self, room_code: str, task_id: str, player_id: str, room: GameRoom) -> Tuple[bool, Optional[str]]:
        """
        Validate if a player can complete a task
        
        Args:
            room_code: Room code
            task_id: Task ID to complete
            player_id: Player attempting completion
            room: Room data
            
        Returns:
            Tuple of (can_complete, error_message)
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return False, "Game not started"
        
        # Check if task exists
        if task_id not in game_state.tasks:
            return False, f"Task {task_id} not found"
        
        task = game_state.tasks[task_id]
        
        # Check if task is assigned to player's role
        player = room.players.get(player_id)
        if not player or player.role != task.assigned_role:
            return False, f"Task {task_id} not assigned to your role"
        
        # Check if task is available
        if task.status != TaskStatus.AVAILABLE and task.status != TaskStatus.IN_PROGRESS:
            return False, f"Task {task_id} is not available (status: {task.status})"
        
        # Check if player is at correct location (discovery/info_share can be done anywhere)
        if task.type not in (TaskType.DISCOVERY, TaskType.INFO_SHARE) and player.location != task.location:
            return False, f"You must be at {task.location} to complete this task"
        
        # Specific validation by task type
        if task.type == TaskType.HANDOFF:
            # Check if player has the item
            has_item = any(item.id == task.handoff_item for item in player.inventory)
            if not has_item:
                return False, f"You don't have {task.handoff_item}"
        
        return True, None
    
    def complete_task(self, room_code: str, task_id: str, player_id: str, room: GameRoom) -> Tuple[bool, List[str], Optional[str]]:
        """
        Complete a task and unlock dependencies
        
        Args:
            room_code: Room code
            task_id: Task ID to complete
            player_id: Player completing task
            room: Room data
            
        Returns:
            Tuple of (success, newly_available_task_ids, error_message)
        """
        # Validate
        can_complete, error = self.can_complete_task(room_code, task_id, player_id, room)
        if not can_complete:
            return False, [], error
        
        game_state = self.get_game_state(room_code)
        task = game_state.tasks[task_id]
        
        # Mark as completed
        task.status = TaskStatus.COMPLETED
        task.assigned_player_id = player_id
        
        # Handle task-specific effects
        if task.type == TaskType.SEARCH:
            # Add found items to player inventory
            player = room.players[player_id]
            for item_name in task.search_items:
                item = Item(
                    id=item_name.lower().replace(" ", "_"),
                    name=item_name,
                    description=f"Found during search at {task.location}"
                )
                player.inventory.append(item)
                logger.info(f"🔍 Player {player_id} found item: {item_name}")
        
        elif task.type == TaskType.HANDOFF:
            # Handle item transfer (if giving, not receiving)
            if task.handoff_item and task.handoff_to_role:
                player = room.players[player_id]
                # Remove item from giver
                player.inventory = [item for item in player.inventory if item.id != task.handoff_item]
                logger.info(f"🤝 Player {player_id} handed off item: {task.handoff_item}")
        
        # Unlock dependent tasks
        newly_available = game_state.complete_task(task_id)
        
        logger.info(f"✅ Task {task_id} completed by player {player_id}, unlocked {len(newly_available)} new tasks")
        
        return True, newly_available, None
    
    def check_search_completions(self, room_code: str, player_id: str, room: GameRoom) -> List[str]:
        """
        Check if any SEARCH tasks for this player are now completable
        based on items in their inventory.
        
        Returns list of task IDs that should be auto-completed.
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return []
        
        player = room.players.get(player_id)
        if not player or not player.role:
            return []
        
        player_item_ids: Set[str] = {item.id for item in player.inventory}
        completable = []
        
        for task in game_state.tasks.values():
            if task.assigned_role != player.role:
                continue
            if task.type != TaskType.SEARCH:
                continue
            if task.status != TaskStatus.AVAILABLE and task.status != TaskStatus.IN_PROGRESS:
                continue
            if not task.search_items:
                continue
            
            # Check if all search_items are in the player's inventory
            if all(item_id in player_item_ids for item_id in task.search_items):
                completable.append(task.id)
        
        return completable
    
    def check_npc_completions(self, room_code: str, player_id: str, room: GameRoom) -> List[str]:
        """
        Check if any NPC_LLM tasks for this player are now completable
        based on achieved outcomes.
        
        Returns list of task IDs that should be auto-completed.
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return []
        
        player = room.players.get(player_id)
        if not player or not player.role:
            return []
        
        # Get all outcomes achieved by this player
        player_outcomes: Set[str] = set(game_state.achieved_outcomes.get(player_id, []))
        completable = []
        
        for task in game_state.tasks.values():
            if task.assigned_role != player.role:
                continue
            if task.type != TaskType.NPC_LLM:
                continue
            if task.status != TaskStatus.AVAILABLE and task.status != TaskStatus.IN_PROGRESS:
                continue
            if not task.target_outcomes:
                continue
            
            # Check if all target_outcomes are achieved
            if all(outcome_id in player_outcomes for outcome_id in task.target_outcomes):
                completable.append(task.id)
        
        return completable
    
    def check_handoff_completions(self, room_code: str, player_id: str, room: GameRoom, transferred_item_id: str) -> List[str]:
        """
        Check if any HANDOFF tasks for this player are now completable
        because they just transferred the required item.
        
        Returns list of task IDs that should be auto-completed.
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return []
        
        player = room.players.get(player_id)
        if not player or not player.role:
            return []
        
        completable = []
        
        for task in game_state.tasks.values():
            if task.assigned_role != player.role:
                continue
            if task.type != TaskType.HANDOFF:
                continue
            if task.status != TaskStatus.AVAILABLE and task.status != TaskStatus.IN_PROGRESS:
                continue
            if task.handoff_item != transferred_item_id:
                continue
            
            completable.append(task.id)
        
        return completable
    
    def auto_complete_task(self, room_code: str, task_id: str, player_id: str, room: GameRoom) -> Tuple[bool, List[str], Optional[str]]:
        """
        Auto-complete a task (no location check -- the triggering event already verified context).
        Skips the SEARCH item-adding side effect since items were already picked up.
        
        Returns (success, newly_available_task_ids, error_message)
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return False, [], "Game not started"
        
        if task_id not in game_state.tasks:
            return False, [], f"Task {task_id} not found"
        
        task = game_state.tasks[task_id]
        
        if task.status == TaskStatus.COMPLETED:
            return False, [], f"Task {task_id} already completed"
        
        # Mark as completed
        task.status = TaskStatus.COMPLETED
        task.assigned_player_id = player_id
        
        # Unlock dependent tasks
        newly_available = game_state.complete_task(task_id)
        
        logger.info(f"✅ Task {task_id} auto-completed by player {player_id}, unlocked {len(newly_available)} new tasks")
        
        return True, newly_available, None
    
    def get_available_tasks_for_player(self, room_code: str, player_id: str, room: GameRoom) -> List[Task]:
        """
        Get all available tasks for a player
        
        Args:
            room_code: Room code
            player_id: Player ID
            room: Room data
            
        Returns:
            List of available tasks
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return []
        
        player = room.players.get(player_id)
        if not player or not player.role:
            return []
        
        return game_state.get_available_tasks_for_role(player.role)
    
    def get_all_tasks_for_player(self, room_code: str, player_id: str, room: GameRoom) -> List[Task]:
        """
        Get ALL tasks (available + locked) for a player
        
        Args:
            room_code: Room code
            player_id: Player ID
            room: Room data
            
        Returns:
            List of all tasks for player's role
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return []
        
        player = room.players.get(player_id)
        if not player or not player.role:
            return []
        
        return game_state.get_tasks_for_role(player.role)
    
    def is_game_won(self, room_code: str) -> bool:
        """
        Check if all tasks are completed (game won)
        
        Args:
            room_code: Room code
            
        Returns:
            True if all tasks completed
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return False
        
        return game_state.is_game_won()
    
    def is_game_lost(self, room_code: str) -> Tuple[bool, Optional[str]]:
        """
        Check if game is lost (time ran out, etc.)
        
        Args:
            room_code: Room code
            
        Returns:
            Tuple of (is_lost, reason)
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return False, None
        
        # Check if time ran out
        if game_state.elapsed_minutes >= game_state.timeline_minutes:
            return True, "Time ran out"
        
        # TODO: Add other failure conditions
        
        return False, None
    
    def update_timer(self, room_code: str, elapsed_minutes: int) -> None:
        """
        Update game timer
        
        Args:
            room_code: Room code
            elapsed_minutes: Minutes elapsed
        """
        game_state = self.get_game_state(room_code)
        if game_state:
            game_state.elapsed_minutes = elapsed_minutes
    
    def get_game_progress(self, room_code: str) -> Dict[str, any]:
        """
        Get game progress statistics
        
        Args:
            room_code: Room code
            
        Returns:
            Dict with progress stats
        """
        game_state = self.get_game_state(room_code)
        if not game_state:
            return {}
        
        total_tasks = len(game_state.tasks)
        completed_tasks = sum(1 for task in game_state.tasks.values() if task.status == TaskStatus.COMPLETED)
        available_tasks = sum(1 for task in game_state.tasks.values() if task.status == TaskStatus.AVAILABLE)
        locked_tasks = sum(1 for task in game_state.tasks.values() if task.status == TaskStatus.LOCKED)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "available_tasks": available_tasks,
            "locked_tasks": locked_tasks,
            "progress_percent": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "elapsed_minutes": game_state.elapsed_minutes,
            "timeline_minutes": game_state.timeline_minutes,
            "time_remaining_minutes": game_state.timeline_minutes - game_state.elapsed_minutes
        }
    
    def cleanup_game_state(self, room_code: str) -> bool:
        """
        Remove game state for a room
        
        Args:
            room_code: Room code
            
        Returns:
            True if removed, False if not found
        """
        if room_code in self.game_states:
            del self.game_states[room_code]
            logger.info(f"🧹 Cleaned up game state for room {room_code}")
            return True
        return False


# Global game state manager instance
_game_state_manager: Optional[GameStateManager] = None


def get_game_state_manager() -> GameStateManager:
    """Get or create global GameStateManager instance"""
    global _game_state_manager
    if _game_state_manager is None:
        _game_state_manager = GameStateManager()
    return _game_state_manager
