"""
Data models for NPC interactions
"""

from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum


class ConfidenceLevel(str, Enum):
    """How confident we are that the NPC knows this information"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ACTION = "action"


class Objective(BaseModel):
    """Information the player is trying to learn"""
    id: str = Field(..., description="Unique identifier for the objective")
    description: str = Field(..., description="What the player needs to learn")
    confidence: ConfidenceLevel = Field(..., description="How likely NPC knows this")
    is_completed: bool = Field(default=False, description="Has this been revealed?")


class NPCInfo(BaseModel):
    """NPC character information"""
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


class ChatRequest(BaseModel):
    """Request to get NPC response"""
    npc: NPCInfo
    objectives: list[Objective]
    player_message: str = Field(..., description="What the player said")
    conversation_history: list[ChatMessage] = Field(default_factory=list)
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium")


class ChatResponse(BaseModel):
    """NPC response to player"""
    text: str = Field(..., description="What the NPC said")
    revealed_objectives: list[str] = Field(
        default_factory=list,
        description="IDs of objectives that were revealed"
    )


class QuickResponsesRequest(BaseModel):
    """Request to generate quick response suggestions"""
    npc: NPCInfo
    objectives: list[Objective]
    conversation_history: list[ChatMessage] = Field(default_factory=list)


class QuickResponsesResponse(BaseModel):
    """Quick response suggestions"""
    responses: list[str] = Field(
        ...,
        description="3 suggested responses for the player",
        min_length=3,
        max_length=3
    )
