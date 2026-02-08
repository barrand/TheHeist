"""
Data models for NPC interactions
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from enum import Enum


class ConfidenceLevel(str, Enum):
    """How confident we are that the NPC knows this information"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ACTION = "action"


class Objective(BaseModel):
    """Information the player is trying to learn (legacy)"""
    id: str = Field(..., description="Unique identifier for the objective")
    description: str = Field(..., description="What the player needs to learn")
    confidence: ConfidenceLevel = Field(..., description="How likely NPC knows this")
    is_completed: bool = Field(default=False, description="Has this been revealed?")


class NPCInfo(BaseModel):
    """NPC character information (legacy)"""
    id: str = Field(..., description="Unique NPC identifier")
    name: str = Field(..., description="NPC's full name")
    role: str = Field(..., description="NPC's job/role")
    personality: str = Field(..., description="Personality description for LLM")
    location: str = Field(..., description="Current location")


class ChatMessage(BaseModel):
    """A single message in the conversation"""
    text: str = Field(..., description="Message content")
    is_player: bool = Field(..., alias="isPlayer", description="True if from player")
    timestamp: str = Field(..., description="ISO timestamp")


# ============================================================
# New conversation system models
# ============================================================

class QuickResponseOption(BaseModel):
    """A quick response option with hidden fit score"""
    text: str = Field(..., description="Response text shown to player")
    fit_score: int = Field(..., description="Cover fit score 1-5 (shown in debug mode)")


class StartConversationRequest(BaseModel):
    """Request to start a conversation with an NPC"""
    npc_id: str = Field(..., description="NPC to talk to")
    cover_id: str = Field(..., description="Chosen cover story ID")
    room_code: str = Field(..., description="Game room code")
    player_id: str = Field(..., description="Player starting the conversation")


class StartConversationResponse(BaseModel):
    """Response when starting a conversation"""
    greeting: str = Field(..., description="NPC's opening line based on cover story")
    quick_responses: List[QuickResponseOption] = Field(..., description="First set of quick response options")
    suspicion: int = Field(default=0, description="Starting suspicion level (always 0)")
    npc_name: str = Field(..., description="NPC display name")
    npc_role: str = Field(..., description="NPC role")
    cover_label: str = Field(..., description="Chosen cover story description")
    info_objectives: List[dict] = Field(default_factory=list, description="Info items player can discover (id + description)")
    action_objectives: List[dict] = Field(default_factory=list, description="Actions player can convince NPC to perform (id + description)")


class ConversationChatRequest(BaseModel):
    """Request to send a chosen quick response"""
    response_index: int = Field(..., description="Index of chosen quick response (0, 1, or 2)")
    room_code: str = Field(..., description="Game room code")
    player_id: str = Field(..., description="Player in conversation")
    npc_id: str = Field(..., description="NPC being talked to")


class ConversationChatResponse(BaseModel):
    """Response from a conversation turn"""
    npc_response: str = Field(..., description="NPC's dialogue")
    outcomes: List[str] = Field(default_factory=list, description="Outcome IDs achieved this turn")
    suspicion: int = Field(..., description="Current suspicion level 0-5")
    suspicion_delta: int = Field(default=0, description="How much suspicion changed this turn")
    quick_responses: List[QuickResponseOption] = Field(default_factory=list, description="Next set of quick responses (empty if conversation ended)")
    conversation_failed: bool = Field(default=False, description="True if suspicion hit 5")
    cooldown_until: Optional[float] = Field(None, description="Epoch timestamp when cooldown expires (if failed)")
    completed_tasks: List[str] = Field(default_factory=list, description="Task IDs that auto-completed from outcomes")


class CooldownStatusResponse(BaseModel):
    """Cooldown status for a player-NPC pair"""
    in_cooldown: bool = Field(..., description="Whether player is in cooldown")
    cooldown_remaining_seconds: Optional[int] = Field(None, description="Seconds remaining if in cooldown")


# ============================================================
# Legacy models (kept for backward compatibility)
# ============================================================

class ChatRequest(BaseModel):
    """Request to get NPC response (legacy)"""
    npc: NPCInfo
    objectives: list[Objective]
    player_message: str = Field(..., description="What the player said")
    conversation_history: list[ChatMessage] = Field(default_factory=list)
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium")


class ChatResponse(BaseModel):
    """NPC response to player (legacy)"""
    text: str = Field(..., description="What the NPC said")
    revealed_objectives: list[str] = Field(
        default_factory=list,
        description="IDs of objectives that were revealed"
    )


class QuickResponsesRequest(BaseModel):
    """Request to generate quick response suggestions (legacy)"""
    npc: NPCInfo
    objectives: list[Objective]
    conversation_history: list[ChatMessage] = Field(default_factory=list)


class QuickResponsesResponse(BaseModel):
    """Quick response suggestions (legacy)"""
    responses: list[str] = Field(
        ...,
        description="3 suggested responses for the player",
        min_length=3,
        max_length=3
    )
