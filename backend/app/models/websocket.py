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


class GameStartedMessage(BaseModel):
    """Broadcast when host starts game"""
    type: Literal["game_started"] = "game_started"
    scenario: str = Field(..., description="Scenario being played")
    objective: str = Field(..., description="Main objective")
    your_tasks: List[Dict] = Field(..., description="Tasks assigned to this player")


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
