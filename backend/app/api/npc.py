"""
NPC API endpoints
Handle NPC conversations and interactions
"""

import logging
from fastapi import APIRouter, HTTPException, Depends

from app.models.npc import (
    ChatRequest,
    ChatResponse,
    QuickResponsesRequest,
    QuickResponsesResponse,
)
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/npc", tags=["npc"])


def get_gemini_service() -> GeminiService:
    """Dependency injection for Gemini service"""
    return GeminiService()


@router.post("/chat", response_model=ChatResponse)
async def npc_chat(
    request: ChatRequest,
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> ChatResponse:
    """
    Get NPC response to player message
    
    - **npc**: NPC information (name, role, personality, location)
    - **objectives**: What the player is trying to learn
    - **player_message**: What the player said
    - **conversation_history**: Previous messages
    - **difficulty**: easy/medium/hard
    
    Returns NPC's response and any revealed objectives
    """
    try:
        logger.info(f"💬 Chat request: {request.npc.name} <- '{request.player_message}'")
        
        # Get NPC response from Gemini
        npc_text = await gemini_service.get_npc_response(
            npc=request.npc,
            objectives=request.objectives,
            player_message=request.player_message,
            difficulty=request.difficulty
        )
        
        # Detect revealed objectives
        revealed = gemini_service.detect_revealed_objectives(
            npc_text=npc_text,
            objectives=request.objectives
        )
        
        if revealed:
            logger.info(f"✅ Revealed objectives: {revealed}")
        
        return ChatResponse(
            text=npc_text,
            revealed_objectives=revealed
        )
        
    except Exception as e:
        logger.error(f"❌ Error in NPC chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get NPC response: {str(e)}"
        )


@router.post("/quick-responses", response_model=QuickResponsesResponse)
async def generate_quick_responses(
    request: QuickResponsesRequest,
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> QuickResponsesResponse:
    """
    Generate 3 quick response suggestions for the player
    
    - **npc**: NPC information
    - **objectives**: What the player is trying to learn
    - **conversation_history**: Previous messages
    
    Returns 3 suggested responses
    """
    try:
        logger.info(f"🎲 Quick responses request for {request.npc.name}")
        
        # Convert Pydantic models to dicts for service
        history_dicts = [msg.model_dump(by_alias=True) for msg in request.conversation_history]
        
        responses = await gemini_service.generate_quick_responses(
            npc=request.npc,
            objectives=request.objectives,
            conversation_history=history_dicts
        )
        
        return QuickResponsesResponse(responses=responses)
        
    except Exception as e:
        logger.error(f"❌ Error generating quick responses: {e}", exc_info=True)
        # Return fallback responses instead of failing
        return QuickResponsesResponse(responses=[
            "Tell me more about your work here.",
            "Have you noticed anything unusual?",
            "How long have you been in this position?",
        ])
