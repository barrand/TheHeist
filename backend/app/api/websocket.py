"""
WebSocket API endpoints for real-time multiplayer
"""

import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any

from app.services.room_manager import get_room_manager
from app.services.websocket_manager import get_ws_manager
from app.services.experience_loader import ExperienceLoader
from app.models.room import RoomStatus
from app.models.websocket import (
    JoinRoomMessage,
    SelectRoleMessage,
    StartGameMessage,
    CompleteTaskMessage,
    NPCMessageRequest,
    MoveLocationMessage,
    HandoffItemMessage,
    PlayerJoinedMessage,
    RoleSelectedMessage,
    GameStartedMessage,
    TaskCompletedMessage,
    PlayerMovedMessage,
    ErrorMessage,
    RoomStateMessage
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    """
    WebSocket endpoint for room communication
    
    Args:
        websocket: WebSocket connection
        room_code: Room code to connect to
    """
    room_manager = get_room_manager()
    ws_manager = get_ws_manager()
    player_id: str = None
    
    try:
        # Accept connection
        await websocket.accept()
        logger.info(f"🔌 WebSocket connection accepted for room {room_code}")
        
        # Wait for initial join message
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "join_room":
                # Handle join room
                player_name = data.get("player_name")
                
                # Get or join room
                room = room_manager.get_room(room_code)
                if not room:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Room {room_code} not found"
                    })
                    await websocket.close()
                    return
                
                # Check if rejoining
                existing_player = None
                for pid, player in room.players.items():
                    if player.name == player_name:
                        existing_player = pid
                        break
                
                if existing_player:
                    # Rejoin as existing player
                    player_id = existing_player
                    room.players[player_id].connected = True
                    logger.info(f"🔄 Player {player_name} ({player_id}) rejoined room {room_code}")
                else:
                    # Join as new player
                    result = room_manager.join_room(room_code, player_name)
                    if not result:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Could not join room"
                        })
                        await websocket.close()
                        return
                    
                    room, player_id = result
                
                # Register WebSocket connection
                await ws_manager.connect(room_code, player_id, websocket)
                
                # Send room state to joining player
                room_state = RoomStateMessage(
                    type="room_state",
                    room_code=room_code,
                    players=[p.model_dump(mode='json') for p in room.players.values()],
                    scenario=room.scenario,
                    status=room.status.value,
                    your_player_id=player_id,
                    is_host=room.is_host(player_id)
                )
                room_state_dict = room_state.model_dump(mode='json')
                logger.info(f"📤 Sending room_state to player {player_id}")
                await websocket.send_json(room_state_dict)
                logger.info(f"✅ room_state sent to player {player_id}")
                
                # If game already in progress, send game_started message to late joiner
                if room.status == RoomStatus.IN_PROGRESS and room.game_state:
                    logger.info(f"🎮 Game already in progress, sending game_started to late joiner {player_id}")
                    
                    # Get player's role
                    player_role = room.players[player_id].role
                    if player_role:
                        # Get tasks for this player's role
                        your_tasks = [
                            task for task in room.game_state.get('tasks', [])
                            if task.get('role') == player_role
                        ]
                        
                        game_started_msg = {
                            "type": "game_started",
                            "scenario": room.scenario,
                            "objective": room.game_state.get('objective', ''),
                            "your_tasks": your_tasks
                        }
                        
                        await websocket.send_json(game_started_msg)
                        logger.info(f"✅ Sent game_started to late joiner {player_id}")
                
                # Broadcast player joined to others
                if existing_player:
                    # Rejoined - no broadcast needed
                    pass
                else:
                    player_joined = PlayerJoinedMessage(
                        type="player_joined",
                        player=room.players[player_id].model_dump(mode='json')
                    )
                    await ws_manager.broadcast_to_room(
                        room_code,
                        player_joined.model_dump(mode='json'),
                        exclude_player=player_id
                    )
                
                break  # Exit initial join loop
        
        # Main message handling loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            logger.info(f"📨 Received {message_type} from player {player_id} in room {room_code}")
            
            # Route message to appropriate handler
            if message_type == "select_role":
                await handle_select_role(room_code, player_id, data)
            
            elif message_type == "start_game":
                await handle_start_game(room_code, player_id, data)
            
            elif message_type == "complete_task":
                await handle_complete_task(room_code, player_id, data)
            
            elif message_type == "npc_message":
                await handle_npc_message(room_code, player_id, data)
            
            elif message_type == "move_location":
                await handle_move_location(room_code, player_id, data)
            
            elif message_type == "handoff_item":
                await handle_handoff_item(room_code, player_id, data)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected for player {player_id} in room {room_code}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    
    finally:
        # Clean up connection
        if player_id:
            ws_manager.disconnect(room_code, player_id)
            
            # Mark player as disconnected
            room = room_manager.get_room(room_code)
            if room and player_id in room.players:
                room.players[player_id].connected = False


async def handle_select_role(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle role selection"""
    room_manager = get_room_manager()
    ws_manager = get_ws_manager()
    
    role = data.get("role")
    
    logger.info(f"🎭 Player {player_id} selecting role: {role} in room {room_code}")
    
    success = room_manager.set_player_role(room_code, player_id, role)
    if not success:
        logger.warning(f"❌ Role selection failed for {player_id} - role {role} (already taken or game started)")
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Could not select role (already taken or game started)"
        })
        return
    
    # Broadcast role selection
    room = room_manager.get_room(room_code)
    player = room.players[player_id]
    
    logger.info(f"✅ Role {role} assigned to {player.name} ({player_id})")
    logger.info(f"📢 Broadcasting role_selected to all players in room {room_code}")
    
    role_selected = RoleSelectedMessage(
        type="role_selected",
        player_id=player_id,
        player_name=player.name,
        role=role
    )
    
    role_dict = role_selected.model_dump(mode='json')
    logger.info(f"📤 Broadcasting role_selected message")
    await ws_manager.broadcast_to_room(room_code, role_dict)


async def handle_start_game(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle game start (host only)"""
    room_manager = get_room_manager()
    ws_manager = get_ws_manager()
    
    scenario = data.get("scenario")
    
    # Start game
    success = room_manager.start_game(room_code, player_id, scenario)
    if not success:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Could not start game (not host, not enough players, or roles not selected)"
        })
        return
    
    # Load experience
    room = room_manager.get_room(room_code)
    selected_roles = room.get_selected_roles()
    
    try:
        loader = ExperienceLoader(experiences_dir="examples")
        game_state = loader.load_experience(scenario, selected_roles)
        
        # Store game state (in room manager for now, will move to game state manager)
        # For now, we'll just broadcast the start
        
        # Send game started to each player with their specific tasks
        for pid, player in room.players.items():
            player_tasks = game_state.get_available_tasks_for_role(player.role)
            
            game_started = GameStartedMessage(
                type="game_started",
                scenario=scenario,
                objective=game_state.objective,
                your_tasks=[task.model_dump(mode='json') for task in player_tasks],
                npcs=[npc.model_dump(mode='json') for npc in game_state.npcs],
                locations=[loc.model_dump(mode='json') for loc in game_state.locations]
            )
            await ws_manager.send_to_player(room_code, pid, game_started.model_dump(mode='json'))
        
        logger.info(f"🎮 Game started in room {room_code} - scenario: {scenario}")
    
    except Exception as e:
        logger.error(f"Error loading experience: {e}", exc_info=True)
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": f"Could not load experience: {str(e)}"
        })


async def handle_complete_task(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle task completion"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    
    task_id = data.get("task_id")
    
    # TODO: Validate task completion with GameStateManager
    # For now, just broadcast
    
    room = room_manager.get_room(room_code)
    player = room.players[player_id]
    
    task_completed = TaskCompletedMessage(
        type="task_completed",
        task_id=task_id,
        by_player_id=player_id,
        by_player_name=player.name,
        newly_available=[]  # Will be filled by GameStateManager
    )
    await ws_manager.broadcast_to_room(room_code, task_completed.model_dump(mode='json'))


async def handle_npc_message(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle NPC conversation message"""
    # TODO: Integrate with NPCConversationService
    # For now, just acknowledge
    pass


async def handle_move_location(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle player location change"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    
    location = data.get("location")
    
    room = room_manager.get_room(room_code)
    if room and player_id in room.players:
        room.players[player_id].location = location
        
        player_moved = PlayerMovedMessage(
            type="player_moved",
            player_id=player_id,
            player_name=room.players[player_id].name,
            location=location
        )
        await ws_manager.broadcast_to_room(room_code, player_moved.model_dump(mode='json'))


async def handle_handoff_item(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle item handoff between players"""
    # TODO: Implement inventory management
    pass
