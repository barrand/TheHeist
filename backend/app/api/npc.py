"""
NPC API endpoints
Handle NPC conversations with cover fit score system
"""

import logging
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from app.models.npc import (
    StartConversationRequest,
    StartConversationResponse,
    ConversationChatRequest,
    ConversationChatResponse,
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


# ============================================================
# Test / Dev endpoints for rapid NPC conversation iteration
# ============================================================

class TestScenarioInfo(BaseModel):
    scenario_id: str
    roles: List[str]
    filename: str

class TestNPCInfo(BaseModel):
    id: str
    name: str
    role: str
    personality: str
    location: str
    cover_options: List[dict]
    target_outcomes: List[str] = Field(default_factory=list)
    task_description: str = ""

class TestSetupResponse(BaseModel):
    room_code: str
    player_id: str
    npcs: List[TestNPCInfo]
    scenario_id: str
    difficulty: str


@router.get("/test-scenarios")
async def list_test_scenarios():
    """List available generated scenarios for testing NPC conversations."""
    experiences_dir = Path(__file__).parent.parent.parent / "experiences"
    scenarios: List[TestScenarioInfo] = []
    for json_file in sorted(experiences_dir.glob("generated_*.json")):
        stem = json_file.stem  # e.g. generated_museum_gala_vault_cat_burglar_safe_cracker
        parts = stem.removeprefix("generated_").split("_")
        # Heuristic: scenario IDs use multi-word names; roles are typically 1-2 words.
        # Load the JSON to get the actual scenario_id and roles.
        import json as _json
        try:
            with open(json_file) as f:
                data = _json.load(f)
            scenario_id = data.get("scenario_id", stem)
            roles = sorted({t["assigned_role"] for t in data.get("tasks", []) if t.get("assigned_role")})
            scenarios.append(TestScenarioInfo(scenario_id=scenario_id, roles=roles, filename=json_file.name))
        except Exception:
            continue
    return scenarios


@router.post("/test-setup")
async def setup_test_conversation(
    scenario_id: str = Query(...),
    roles: str = Query(..., description="Comma-separated roles, e.g. cat_burglar,safe_cracker"),
    difficulty: str = Query("easy"),
):
    """
    Create a temporary room + game state for testing NPC conversations.
    Returns room_code, player_id, and NPC list so the frontend can use
    the normal /start-conversation and /chat endpoints.
    """
    from app.services.experience_loader import ExperienceLoader, scenario_cache_filename
    from app.models.room import GameRoom, Player, RoomStatus

    role_list = [r.strip() for r in roles.split(",")]
    loader = ExperienceLoader(experiences_dir="experiences")

    try:
        game_state = loader.load_experience(scenario_id, role_list)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not load scenario: {e}")

    # Create a temporary room with a test player
    import random as _rand
    room_code = "T" + "".join(_rand.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=4))
    player_id = f"test_{uuid.uuid4().hex[:8]}"
    test_player = Player(
        id=player_id,
        name="NPC Tester",
        role=role_list[0],
        difficulty=difficulty,
    )
    room = GameRoom(
        room_code=room_code,
        host_id=player_id,
        players={player_id: test_player},
        scenario=scenario_id,
        status=RoomStatus.IN_PROGRESS,
    )

    # Register the room and game state so the conversation endpoints can find them
    room_mgr = get_room_manager()
    room_mgr.rooms[room_code] = room

    game_state_mgr = get_game_state_manager()
    game_state_mgr.game_states[room_code] = game_state

    # Build NPC list with associated task info
    npcs: List[TestNPCInfo] = []
    for npc in game_state.npcs:
        # Find tasks that target this NPC
        outcome_set: set = set()
        task_desc = ""
        for task in game_state.tasks.values():
            if getattr(task, "npc_id", None) == npc.id:
                for o in (task.target_outcomes or []):
                    outcome_set.add(o)
                if not task_desc:
                    task_desc = task.description
        target_outcomes = sorted(outcome_set)

        npcs.append(TestNPCInfo(
            id=npc.id,
            name=npc.name,
            role=npc.role,
            personality=npc.personality,
            location=npc.location,
            cover_options=[c.model_dump() for c in npc.cover_options],
            target_outcomes=target_outcomes,
            task_description=task_desc,
        ))

    logger.info(f"🧪 Test session created: room={room_code} player={player_id} scenario={scenario_id} npcs={[n.name for n in npcs]}")

    return TestSetupResponse(
        room_code=room_code,
        player_id=player_id,
        npcs=npcs,
        scenario_id=scenario_id,
        difficulty=difficulty,
    )


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
        difficulty = getattr(player, 'difficulty', 'medium') if player else 'medium'
        
        # Find NPC
        npc = game_state.get_npc_by_id(request.npc_id)
        if not npc:
            raise HTTPException(status_code=404, detail=f"NPC {request.npc_id} not found")
        
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
            suspicion=suspicion,  # compat: now holds rapport value
            rapport=suspicion,
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
         completed_tasks, opening_given) = npc_service.process_player_choice(
            response_index=request.response_index,
            player_id=request.player_id,
            npc=npc,
            difficulty=difficulty,
            game_state=game_state,
        )
        
        logger.info(f"💬 Chat turn: rapport={suspicion} (delta={suspicion_delta:+d}) | outcomes={outcomes} | failed={conversation_failed}")
        
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
            suspicion=suspicion,           # compat: now holds rapport
            suspicion_delta=suspicion_delta,  # compat: now holds rapport_delta*10
            rapport=suspicion,
            rapport_delta=suspicion_delta,
            quick_responses=quick_responses,
            conversation_failed=conversation_failed,
            cooldown_until=cooldown_until,
            completed_tasks=completed_tasks,
            opening_given=opening_given,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in conversation chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))




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
