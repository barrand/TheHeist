"""Pydantic data models for request/response validation"""

from .npc import (
    Objective,
    NPCInfo,
    ChatRequest,
    ChatResponse,
    QuickResponsesRequest,
    QuickResponsesResponse,
    ConfidenceLevel,
)

from .room import (
    RoomStatus,
    Item,
    Player,
    GameRoom,
)

from .game_state import (
    TaskType,
    TaskStatus,
    PrerequisiteType,
    Prerequisite,
    Location,
    Task,
    NPCInfoItem,
    NPCAction,
    NPCCoverOption,
    NPCData,
    Item as GameItem,
    GameState,
)

from .websocket import (
    JoinRoomMessage,
    SelectRoleMessage,
    StartGameMessage,
    CompleteTaskMessage,
    NPCMessageRequest,
    MoveLocationMessage,
    HandoffItemMessage,
    PlayerJoinedMessage,
    PlayerLeftMessage,
    RoleSelectedMessage,
    GameStartedMessage,
    TaskUnlockedMessage,
    TaskCompletedMessage,
    NPCResponseMessage,
    PlayerMovedMessage,
    GameEndedMessage,
    ErrorMessage,
    RoomStateMessage,
)

__all__ = [
    # NPC models
    "Objective",
    "NPCInfo",
    "ChatRequest",
    "ChatResponse",
    "QuickResponsesRequest",
    "QuickResponsesResponse",
    "ConfidenceLevel",
    # Room models
    "RoomStatus",
    "Item",
    "Player",
    "GameRoom",
    # Game state models
    "TaskType",
    "TaskStatus",
    "PrerequisiteType",
    "Prerequisite",
    "Location",
    "Task",
    "NPCInfoItem",
    "NPCAction",
    "NPCCoverOption",
    "NPCData",
    "GameItem",
    "GameState",
    # WebSocket messages
    "JoinRoomMessage",
    "SelectRoleMessage",
    "StartGameMessage",
    "CompleteTaskMessage",
    "NPCMessageRequest",
    "MoveLocationMessage",
    "HandoffItemMessage",
    "PlayerJoinedMessage",
    "PlayerLeftMessage",
    "RoleSelectedMessage",
    "GameStartedMessage",
    "TaskUnlockedMessage",
    "TaskCompletedMessage",
    "NPCResponseMessage",
    "PlayerMovedMessage",
    "GameEndedMessage",
    "ErrorMessage",
    "RoomStateMessage",
]
