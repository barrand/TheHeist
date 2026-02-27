"""
WebSocket message schemas for real-time communication
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Literal


# ============================================
# Client → Server Messages
# ============================================

class JoinRoomMessage(BaseModel):
    """Player wants to join a room"""
    type: Literal["join_room"] = "join_room"
    room_code: str = Field(..., description="4-5 letter room code (e.g., 'APPLE', 'TIGER')")
    player_name: str = Field(..., description="Player's display name")


class SelectRoleMessage(BaseModel):
    """Player selects their role in lobby"""
    type: Literal["select_role"] = "select_role"
    role: str = Field(..., description="Selected role (mastermind, hacker, etc.)")


class StartGameMessage(BaseModel):
    """Host starts the game"""
    type: Literal["start_game"] = "start_game"
    scenario: str = Field(..., description="Selected scenario ID")


class CompleteTaskMessage(BaseModel):
    """Player completed a task"""
    type: Literal["complete_task"] = "complete_task"
    task_id: str = Field(..., description="ID of completed task")


class NPCMessageRequest(BaseModel):
    """Player sends message to NPC"""
    type: Literal["npc_message"] = "npc_message"
    task_id: str = Field(..., description="Task ID for this conversation")
    npc_id: str = Field(..., description="NPC to talk to")
    message: str = Field(..., description="What player said")


class MoveLocationMessage(BaseModel):
    """Player moves to new location"""
    type: Literal["move_location"] = "move_location"
    location: str = Field(..., description="New location name")


class HandoffItemMessage(BaseModel):
    """Player hands item to another player"""
    type: Literal["handoff_item"] = "handoff_item"
    item_id: str = Field(..., description="Item being transferred")
    to_player_id: str = Field(..., description="Recipient player ID")


class SearchRoomMessage(BaseModel):
    """Player searches their current room for items"""
    type: Literal["search_room"] = "search_room"


class PickupItemMessage(BaseModel):
    """Player picks up an item from search results"""
    type: Literal["pickup_item"] = "pickup_item"
    item_id: str = Field(..., description="Item to pick up")


class UseItemMessage(BaseModel):
    """Player attempts to use an item"""
    type: Literal["use_item"] = "use_item"
    item_id: str = Field(..., description="Item to use")


class DropItemMessage(BaseModel):
    """Player drops an item in current location"""
    type: Literal["drop_item"] = "drop_item"
    item_id: str = Field(..., description="Item to drop")


# ============================================
# Server → Client Messages
# ============================================

class PlayerJoinedMessage(BaseModel):
    """Broadcast when player joins room"""
    type: Literal["player_joined"] = "player_joined"
    player: Dict = Field(..., description="Player data")


class PlayerLeftMessage(BaseModel):
    """Broadcast when player leaves room"""
    type: Literal["player_left"] = "player_left"
    player_id: str = Field(..., description="Player who left")
    player_name: str = Field(..., description="Player's name")


class RoleSelectedMessage(BaseModel):
    """Broadcast when player selects role"""
    type: Literal["role_selected"] = "role_selected"
    player_id: str = Field(..., description="Player who selected")
    player_name: str = Field(..., description="Player's name")
    role: str = Field(..., description="Selected role")
    difficulty: str = Field(default="easy", description="Player's difficulty setting")


class GameStartedMessage(BaseModel):
    """Broadcast when host starts game"""
    type: Literal["game_started"] = "game_started"
    scenario: str = Field(..., description="Scenario being played")
    objective: str = Field(..., description="Main objective")
    your_tasks: List[Dict] = Field(..., description="Tasks assigned to this player")
    npcs: List[Dict] = Field(default_factory=list, description="All NPCs in the scenario")
    locations: List[Dict] = Field(default_factory=list, description="All locations in the scenario")
    starting_location: str = Field(..., description="Player's starting location")


class TaskUnlockedMessage(BaseModel):
    """Notify player that new task is available"""
    type: Literal["task_unlocked"] = "task_unlocked"
    task: Dict = Field(..., description="Newly available task")


class TaskCompletedMessage(BaseModel):
    """Broadcast when task is completed"""
    type: Literal["task_completed"] = "task_completed"
    task_id: str = Field(..., description="ID of completed task")
    by_player_id: str = Field(..., description="Who completed it")
    by_player_name: str = Field(..., description="Player's name")
    newly_available: List[str] = Field(default_factory=list, description="Newly unlocked task IDs")
    achieved_outcomes: List[str] = Field(default_factory=list, description="Outcome IDs achieved by this task")


class NPCResponseMessage(BaseModel):
    """NPC response to player message"""
    type: Literal["npc_response"] = "npc_response"
    to_player_id: str = Field(..., description="Player who gets this")
    task_id: str = Field(..., description="Associated task")
    text: str = Field(..., description="What NPC said")
    revealed_objectives: List[str] = Field(default_factory=list, description="Objectives revealed")


class PlayerMovedMessage(BaseModel):
    """Broadcast when player moves location"""
    type: Literal["player_moved"] = "player_moved"
    player_id: str = Field(..., description="Player who moved")
    player_name: str = Field(..., description="Player's name")
    location: str = Field(..., description="New location")


class GameEndedMessage(BaseModel):
    """Broadcast when game ends"""
    type: Literal["game_ended"] = "game_ended"
    result: Literal["success", "failure"] = Field(..., description="Did team win?")
    summary: str = Field(..., description="End game summary text")
    objective: Optional[str] = Field(None, description="Original heist objective")
    scenario: Optional[str] = Field(None, description="Scenario name")


class ErrorMessage(BaseModel):
    """Error response to client"""
    type: Literal["error"] = "error"
    message: str = Field(..., description="Error description")
    code: Optional[str] = Field(None, description="Error code for handling")


class RoomStateMessage(BaseModel):
    """Full room state (sent on join/reconnect)"""
    type: Literal["room_state"] = "room_state"
    room_code: str
    players: List[Dict]
    scenario: Optional[str]
    status: str
    your_player_id: str
    is_host: bool


class SearchResultsMessage(BaseModel):
    """Results from searching a room"""
    type: Literal["search_results"] = "search_results"
    location: str = Field(..., description="Location searched")
    items: List[Dict] = Field(..., description="Items found")


class ItemPickedUpMessage(BaseModel):
    """Broadcast when player picks up an item"""
    type: Literal["item_picked_up"] = "item_picked_up"
    player_id: str = Field(..., description="Player who picked it up")
    player_name: str = Field(..., description="Player's name")
    item: Dict = Field(..., description="Item data")


class ItemTransferredMessage(BaseModel):
    """Broadcast when item is transferred between players"""
    type: Literal["item_transferred"] = "item_transferred"
    from_player_id: str
    from_player_name: str
    to_player_id: str
    to_player_name: str
    item: Dict
