"""
NPC API endpoints
Handle NPC conversations with cover fit score system
"""

import logging
import time
from fastapi import APIRouter, HTTPException

from app.models.npc import (
    StartConversationRequest,
    StartConversationResponse,
    ConversationChatRequest,
    ConversationChatResponse,
    CooldownStatusResponse,
    QuickResponseOption,
    # Legacy
    ChatRequest,
    ChatResponse,
    QuickResponsesRequest,
    QuickResponsesResponse,
)
from app.services.npc_conversation_service import get_npc_conversation_service
from app.services.game_state_manager import get_game_state_manager
from app.services.room_manager import get_room_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/npc", tags=["npc"])


@router.post("/start-conversation", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest) -> StartConversationResponse:
    """
    Start a conversation with an NPC by choosing a cover story.
    
    Returns NPC greeting, first quick responses, and conversation objectives.
    """
    try:
        npc_service = get_npc_conversation_service()
        game_state_mgr = get_game_state_manager()
        room_mgr = get_room_manager()
        
        # Get game state and room
        game_state = game_state_mgr.get_game_state(request.room_code)
        if not game_state:
            raise HTTPException(status_code=404, detail="Game not started")
        
        room = room_mgr.get_room(request.room_code)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Get player difficulty
        player = room.players.get(request.player_id)
        difficulty = getattr(player, 'difficulty', 'easy') if player else 'easy'
        
        # Find NPC
        npc = game_state.get_npc_by_id(request.npc_id)
        if not npc:
            raise HTTPException(status_code=404, detail=f"NPC {request.npc_id} not found")
        
        # Check cooldown
        in_cooldown, remaining = npc_service.check_cooldown(
            request.player_id, request.npc_id, game_state
        )
        if in_cooldown:
            raise HTTPException(
                status_code=429,
                detail=f"NPC is cooling down. Try again in {remaining} seconds."
            )
        
        # Start conversation
        greeting, quick_responses, suspicion = npc_service.start_conversation(
            npc=npc,
            cover_id=request.cover_id,
            player_id=request.player_id,
            difficulty=difficulty,
            game_state=game_state,
            target_outcomes=request.target_outcomes,
        )
        
        # Build objectives for frontend - only the outcomes the player's task needs
        # If no target_outcomes, this is a "flavor" conversation with no tracked objectives
        cover = next((c for c in npc.cover_options if c.cover_id == request.cover_id), None)
        needed = set(request.target_outcomes) if request.target_outcomes else set()
        
        # Use a short label from the outcome ID, NOT the full secret description
        def _outcome_label(outcome_id: str) -> str:
            return outcome_id.replace("_", " ").title()
        
        info_objectives = [
            {"id": i.info_id, "description": _outcome_label(i.info_id)}
            for i in npc.information_known
            if i.info_id and i.info_id in needed
        ]
        action_objectives = [
            {"id": a.action_id, "description": _outcome_label(a.action_id)}
            for a in npc.actions_available
            if a.action_id in needed
        ]
        
        logger.info(f"💬 Conversation started: {request.player_id} -> {npc.name} as '{request.cover_id}'")
        
        return StartConversationResponse(
            greeting=greeting,
            quick_responses=quick_responses,
            suspicion=suspicion,
            npc_name=npc.name,
            npc_role=npc.role,
            cover_label=cover.description if cover else "Unknown cover",
            info_objectives=info_objectives,
            action_objectives=action_objectives,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ConversationChatResponse)
async def conversation_chat(request: ConversationChatRequest) -> ConversationChatResponse:
    """
    Send a chosen quick response in an active conversation.
    
    The backend looks up the fit score, calculates suspicion, gets NPC response,
    and returns the next set of quick responses.
    """
    try:
        npc_service = get_npc_conversation_service()
        game_state_mgr = get_game_state_manager()
        room_mgr = get_room_manager()
        
        game_state = game_state_mgr.get_game_state(request.room_code)
        if not game_state:
            raise HTTPException(status_code=404, detail="Game not started")
        
        room = room_mgr.get_room(request.room_code)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        player = room.players.get(request.player_id)
        difficulty = getattr(player, 'difficulty', 'easy') if player else 'easy'
        
        npc = game_state.get_npc_by_id(request.npc_id)
        if not npc:
            raise HTTPException(status_code=404, detail=f"NPC {request.npc_id} not found")
        
        # Process the player's choice
        (npc_response, outcomes, suspicion, suspicion_delta, 
         quick_responses, conversation_failed, cooldown_until, 
         completed_tasks) = npc_service.process_player_choice(
            response_index=request.response_index,
            player_id=request.player_id,
            npc=npc,
            difficulty=difficulty,
            game_state=game_state,
        )
        
        logger.info(f"💬 Chat turn: suspicion={suspicion} (delta={suspicion_delta:+d}) | outcomes={outcomes} | failed={conversation_failed}")
        
        # Check for NPC task auto-completions via GameStateManager
        if outcomes:
            from app.services.websocket_manager import get_ws_manager
            from app.models.websocket import TaskCompletedMessage, TaskUnlockedMessage
            ws_manager = get_ws_manager()
            
            completable = game_state_mgr.check_npc_completions(request.room_code, request.player_id, room)
            for task_id in completable:
                success, newly_available, error = game_state_mgr.auto_complete_task(
                    request.room_code, task_id, request.player_id, room
                )
                if success:
                    completed_tasks.append(task_id)
                    # Include the outcomes this task achieved
                    task_obj = game_state.tasks.get(task_id)
                    task_outcomes = list(task_obj.target_outcomes) if task_obj and task_obj.target_outcomes else []
                    task_completed_msg = TaskCompletedMessage(
                        type="task_completed",
                        task_id=task_id,
                        by_player_id=request.player_id,
                        by_player_name=player.name if player else "Unknown",
                        newly_available=newly_available,
                        achieved_outcomes=task_outcomes,
                    )
                    await ws_manager.broadcast_to_room(request.room_code, task_completed_msg.model_dump(mode='json'))
                    
                    # Send newly unlocked tasks to appropriate players
                    for new_task_id in newly_available:
                        new_task = game_state.tasks.get(new_task_id)
                        if new_task:
                            for pid, p in room.players.items():
                                if p.role == new_task.assigned_role:
                                    unlocked_msg = TaskUnlockedMessage(
                                        type="task_unlocked",
                                        task=new_task.model_dump(mode='json')
                                    )
                                    await ws_manager.send_to_player(request.room_code, pid, unlocked_msg.model_dump(mode='json'))
            
            # Re-check all locked tasks: outcomes may unlock tasks with OUTCOME prerequisites
            # even if no NPC_LLM task was auto-completed (idempotent -- already-unlocked tasks are skipped)
            outcome_unlocks = game_state._check_unlocks(request.player_id, room=room)
            for new_task_id in outcome_unlocks:
                new_task = game_state.tasks.get(new_task_id)
                if new_task:
                    for pid, p in room.players.items():
                        if p.role == new_task.assigned_role:
                            unlocked_msg = TaskUnlockedMessage(
                                type="task_unlocked",
                                task=new_task.model_dump(mode='json')
                            )
                            await ws_manager.send_to_player(request.room_code, pid, unlocked_msg.model_dump(mode='json'))
        
        return ConversationChatResponse(
            npc_response=npc_response,
            outcomes=outcomes,
            suspicion=suspicion,
            suspicion_delta=suspicion_delta,
            quick_responses=quick_responses,
            conversation_failed=conversation_failed,
            cooldown_until=cooldown_until,
            completed_tasks=completed_tasks,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in conversation chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cooldown-status/{npc_id}", response_model=CooldownStatusResponse)
async def get_cooldown_status(
    npc_id: str,
    room_code: str,
    player_id: str,
) -> CooldownStatusResponse:
    """Check if a player is in cooldown for a specific NPC"""
    try:
        npc_service = get_npc_conversation_service()
        game_state_mgr = get_game_state_manager()
        
        game_state = game_state_mgr.get_game_state(room_code)
        if not game_state:
            return CooldownStatusResponse(in_cooldown=False)
        
        in_cooldown, remaining = npc_service.check_cooldown(player_id, npc_id, game_state)
        
        return CooldownStatusResponse(
            in_cooldown=in_cooldown,
            cooldown_remaining_seconds=remaining if in_cooldown else None,
        )
    except Exception as e:
        logger.error(f"Error checking cooldown: {e}")
        return CooldownStatusResponse(in_cooldown=False)


# ============================================================
# Legacy endpoints (kept for backward compatibility)
# ============================================================

@router.post("/legacy/chat", response_model=ChatResponse)
async def npc_chat_legacy(request: ChatRequest) -> ChatResponse:
    """Legacy chat endpoint"""
    # Import old service behavior
    from app.services.npc_conversation_service import get_npc_conversation_service
    service = get_npc_conversation_service()
    
    try:
        npc_text = service._call_llm(
            f"You are {request.npc.name}. Respond to: {request.player_message}",
            service.npc_model
        )
        return ChatResponse(text=npc_text, revealed_objectives=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/legacy/quick-responses", response_model=QuickResponsesResponse)
async def generate_quick_responses_legacy(request: QuickResponsesRequest) -> QuickResponsesResponse:
    """Legacy quick responses endpoint"""
    return QuickResponsesResponse(responses=[
        "Tell me more about your work here.",
        "Have you noticed anything unusual?",
        "How long have you been in this position?",
    ])
