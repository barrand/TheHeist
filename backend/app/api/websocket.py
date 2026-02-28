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
from app.services.game_state_manager import get_game_state_manager
from app.models.room import RoomStatus
from app.models.websocket import (
    JoinRoomMessage,
    SelectRoleMessage,
    StartGameMessage,
    CompleteTaskMessage,
    NPCMessageRequest,
    MoveLocationMessage,
    HandoffItemMessage,
    SearchRoomMessage,
    PickupItemMessage,
    PlayerJoinedMessage,
    RoleSelectedMessage,
    GameStartedMessage,
    TaskCompletedMessage,
    TaskUnlockedMessage,
    PlayerMovedMessage,
    SearchResultsMessage,
    ItemPickedUpMessage,
    ItemTransferredMessage,
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
                
                # Get or create room (for E2E testing)
                room = room_manager.get_room(room_code)
                if not room:
                    # Auto-create room if it doesn't exist (E2E testing support)
                    # First joiner will become host
                    from app.models.room import GameRoom
                    from app.models.room import RoomStatus as RoomStatusEnum
                    room = GameRoom(
                        room_code=room_code,
                        host_id="",  # Will be assigned to first joiner
                        players={},
                        status=RoomStatusEnum.LOBBY
                    )
                    room_manager.rooms[room_code] = room
                    logger.info(f"✨ Auto-created room {room_code} for first joiner {player_name}")
                
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
            
            elif message_type == "search_room":
                await handle_search_room(room_code, player_id, data)
            
            elif message_type == "pickup_item":
                await handle_pickup_item(room_code, player_id, data)
            
            elif message_type == "use_item":
                await handle_use_item(room_code, player_id, data)
            
            elif message_type == "drop_item":
                await handle_drop_item(room_code, player_id, data)
            
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
    """Handle role selection (with optional difficulty)"""
    room_manager = get_room_manager()
    ws_manager = get_ws_manager()
    
    role = data.get("role")
    difficulty = data.get("difficulty", "easy")
    
    logger.info(f"🎭 Player {player_id} selecting role: {role} (difficulty: {difficulty}) in room {room_code}")
    
    success = room_manager.set_player_role(room_code, player_id, role)
    if not success:
        logger.warning(f"❌ Role selection failed for {player_id} - role {role} (already taken or game started)")
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Could not select role (already taken or game started)"
        })
        return
    
    # Set difficulty and broadcast role selection
    room = room_manager.get_room(room_code)
    player = room.players[player_id]
    player.difficulty = difficulty
    
    logger.info(f"✅ Role {role} (difficulty: {difficulty}) assigned to {player.name} ({player_id})")
    logger.info(f"📢 Broadcasting role_selected to all players in room {room_code}")
    
    role_selected = RoleSelectedMessage(
        type="role_selected",
        player_id=player_id,
        player_name=player.name,
        role=role,
        difficulty=difficulty
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
    
    # Load experience — generate on the fly if the file doesn't exist yet
    room = room_manager.get_room(room_code)
    selected_roles = room.get_selected_roles()
    
    try:
        loader = ExperienceLoader(experiences_dir="experiences")

        # Check if the experience file exists for this exact scenario + role combo
        from app.services.experience_loader import scenario_cache_filename
        cache_base = scenario_cache_filename(scenario, selected_roles)
        md_file = loader.experiences_dir / (cache_base + ".md")
        json_file = loader.experiences_dir / (cache_base + ".json")
        if not md_file.exists() and not json_file.exists():
            from app.services.scenario_generator_service import generate_scenario

            async def _broadcast(msg: str):
                await ws_manager.broadcast_to_room(room_code, {
                    "type": "scenario_generating",
                    "message": msg
                })

            ok = await generate_scenario(scenario, selected_roles, _broadcast)
            if not ok:
                await ws_manager.send_to_player(room_code, player_id, {
                    "type": "error",
                    "message": "Scenario generation failed. Please try again."
                })
                return

        game_state = loader.load_experience(scenario, selected_roles)
        
        # Store game state in game state manager
        game_state_manager = get_game_state_manager()
        game_state_manager.set_game_state(room_code, game_state)
        
        # Set all players to the starting location (first location in scenario)
        if game_state.locations:
            starting_location = game_state.locations[0].id
            logger.info(f"🏠 Setting all players to starting location: {starting_location}")
            for player in room.players.values():
                player.location = starting_location
                logger.info(f"  📍 {player.name} ({player.role}) → {starting_location}")
        
        # Skip image generation if requested (for E2E testing)
        skip_images = data.get("skip_images", False)
        
        if not skip_images:
            from app.services.image_generator import generate_all_images_for_experience
            experience_dict = {
                'locations': [loc.model_dump() for loc in game_state.locations],
                'items_by_location': {
                    loc: [item.model_dump() for item in items]
                    for loc, items in game_state.items_by_location.items()
                },
                'npcs': [npc.model_dump() for npc in game_state.npcs]
            }

            async def _img_broadcast(msg: str):
                await ws_manager.broadcast_to_room(room_code, {
                    "type": "scenario_generating",
                    "message": msg,
                })

            logger.info(f"🎨 Starting image generation for {scenario}...")
            success = await generate_all_images_for_experience(
                scenario, experience_dict, broadcast=_img_broadcast
            )
            
            if success:
                logger.info(f"✅ Image generation complete for {scenario}")
            else:
                logger.warning(f"⚠️ Image generation had errors for {scenario}, continuing anyway")
        else:
            logger.info(f"⏭️  Skipping image generation (E2E testing mode)")
        
        # Send game started to each player with their specific tasks
        for pid, player in room.players.items():
            player_tasks = game_state.get_available_tasks_for_role(player.role)
            task_ids = [t.id for t in player_tasks]
            logger.info(f"📋 Player {player.role} starting with {len(task_ids)} tasks: {task_ids}")
            
            game_started = GameStartedMessage(
                type="game_started",
                scenario=scenario,
                objective=game_state.objective,
                your_tasks=[task.model_dump(mode='json') for task in player_tasks],
                npcs=[npc.model_dump(mode='json') for npc in game_state.npcs],
                locations=[loc.model_dump(mode='json') for loc in game_state.locations],
                starting_location=player.location
            )
            logger.info(f"📍 Sending {len(game_state.locations)} locations to player {pid} (starting at {player.location})")
            await ws_manager.send_to_player(room_code, pid, game_started.model_dump(mode='json'))
        
        logger.info(f"🎮 Game started in room {room_code} - scenario: {scenario}")
    
    except Exception as e:
        logger.error(f"Error loading experience: {e}", exc_info=True)
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": f"Could not load experience: {str(e)}"
        })


async def handle_complete_task(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle task completion (for manual-complete types: INFO_SHARE, MINIGAME)"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    game_state_manager = get_game_state_manager()
    
    task_id = data.get("task_id")
    
    room = room_manager.get_room(room_code)
    if not room or player_id not in room.players:
        return
    
    player = room.players[player_id]
    
    # Validate and complete via GameStateManager (auto-detects E2E mode)
    success, newly_available, error = game_state_manager.complete_task(
        room_code, task_id, player_id, room
    )
    
    if not success:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": error or f"Cannot complete task {task_id}"
        })
        return
    
    # Broadcast task completed
    await _broadcast_task_completed(room_code, task_id, player_id, player.name, newly_available)
    
    # Also check for item-based unlocks (tasks that depend on items in inventory)
    player_item_ids = {inv_item.id for inv_item in player.inventory}
    game_state = game_state_manager.get_game_state(room_code)
    if game_state:
        item_unlocks = game_state.check_unlocks_with_items(player_item_ids)
        for new_task_id in item_unlocks:
            new_task = game_state.tasks.get(new_task_id)
            if new_task:
                for pid, p in room.players.items():
                    if p.role == new_task.assigned_role:
                        from app.models.websocket import TaskUnlockedMessage
                        unlocked_msg = TaskUnlockedMessage(
                            type="task_unlocked",
                            task=new_task.model_dump(mode='json')
                        )
                        await ws_manager.send_to_player(room_code, pid, unlocked_msg.model_dump(mode='json'))
                logger.info(f"🔓 Task {new_task_id} unlocked (ITEM prerequisite met after task {task_id} completion)")


async def _broadcast_task_completed(
    room_code: str, task_id: str, player_id: str, player_name: str, newly_available: list,
    achieved_outcomes: list = None
) -> None:
    """Broadcast task completion and send newly unlocked tasks to appropriate players"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    game_state_manager = get_game_state_manager()
    
    task_completed = TaskCompletedMessage(
        type="task_completed",
        task_id=task_id,
        by_player_id=player_id,
        by_player_name=player_name,
        newly_available=newly_available,
        achieved_outcomes=achieved_outcomes or [],
    )
    await ws_manager.broadcast_to_room(room_code, task_completed.model_dump(mode='json'))
    
    # Send newly unlocked tasks to the players whose roles match
    if newly_available:
        room = room_manager.get_room(room_code)
        game_state = game_state_manager.get_game_state(room_code)
        if room and game_state:
            for new_task_id in newly_available:
                new_task = game_state.tasks.get(new_task_id)
                if not new_task:
                    continue
                # Find player(s) with this role and send them the task
                for pid, p in room.players.items():
                    if p.role == new_task.assigned_role:
                        unlocked_msg = TaskUnlockedMessage(
                            type="task_unlocked",
                            task=new_task.model_dump(mode='json')
                        )
                        await ws_manager.send_to_player(room_code, pid, unlocked_msg.model_dump(mode='json'))
    
    logger.info(f"✅ Task {task_id} completed by {player_name}, unlocked {len(newly_available)} tasks")


async def handle_npc_message(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle NPC conversation message"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    game_state_manager = get_game_state_manager()
    
    task_id = data.get("task_id")
    npc_id = data.get("npc_id")
    message = data.get("message", "")
    
    logger.info(f"💬 NPC message from {player_id} to {npc_id} for task {task_id}: {message[:50]}...")
    
    room = room_manager.get_room(room_code)
    if not room or player_id not in room.players:
        return
    
    player = room.players[player_id]
    
    # For player role NPCs (ending with _player), auto-complete the task
    # In real game, this would involve actual NPC conversation logic
    if npc_id and npc_id.endswith("_player"):
        logger.info(f"📩 Player NPC task - auto-completing {task_id}")
        
        # Complete the task
        success, newly_available, error = game_state_manager.complete_task(
            room_code, task_id, player_id, room
        )
        
        if success:
            # Send acknowledgment
            await ws_manager.send_to_player(room_code, player_id, {
                "type": "npc_response",
                "task_id": task_id,
                "npc_id": npc_id,
                "text": f"Got it! Let's proceed with the plan.",
                "success": True
            })
            
            # Broadcast task completion
            await _broadcast_task_completed(room_code, task_id, player_id, player.name, newly_available)
        else:
            await ws_manager.send_to_player(room_code, player_id, {
                "type": "error",
                "message": error or f"Cannot complete NPC task {task_id}"
            })
    else:
        # For AI NPCs, would integrate with NPCConversationService
        # For now, just acknowledge
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "npc_response",
            "task_id": task_id,
            "npc_id": npc_id,
            "text": "I understand.",
            "success": False
        })


async def handle_move_location(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle player location change"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    
    location = data.get("location")
    
    room = room_manager.get_room(room_code)
    if room and player_id in room.players:
        # Normalize location to lowercase for consistent comparison with task locations
        room.players[player_id].location = location.lower() if location else location
        
        player_moved = PlayerMovedMessage(
            type="player_moved",
            player_id=player_id,
            player_name=room.players[player_id].name,
            location=location
        )
        await ws_manager.broadcast_to_room(room_code, player_moved.model_dump(mode='json'))


async def handle_handoff_item(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle item handoff between players"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    
    item_id = data.get("item_id")
    to_player_id = data.get("to_player_id")
    
    room = room_manager.get_room(room_code)
    if not room or player_id not in room.players or to_player_id not in room.players:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Invalid transfer request"
        })
        return
    
    from_player = room.players[player_id]
    to_player = room.players[to_player_id]
    
    # Check if both players are in same location (case-insensitive)
    if from_player.location.lower() != to_player.location.lower():
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Players must be in same location to transfer items"
        })
        return
    
    # Find item in from_player's inventory
    item = None
    for i, inv_item in enumerate(from_player.inventory):
        if inv_item.id == item_id:
            item = from_player.inventory.pop(i)
            break
    
    if not item:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Item not found in your inventory"
        })
        return
    
    # Add to to_player's inventory
    to_player.inventory.append(item)
    
    # Broadcast transfer
    transfer_msg = ItemTransferredMessage(
        type="item_transferred",
        from_player_id=player_id,
        from_player_name=from_player.name,
        to_player_id=to_player_id,
        to_player_name=to_player.name,
        item=item.model_dump(mode='json')
    )
    await ws_manager.broadcast_to_room(room_code, transfer_msg.model_dump(mode='json'))
    
    # Auto-complete any HANDOFF tasks for the giving player
    game_state_manager = get_game_state_manager()
    completable_tasks = game_state_manager.check_handoff_completions(
        room_code, player_id, room, item_id
    )
    for task_id in completable_tasks:
        success, newly_available, error = game_state_manager.auto_complete_task(
            room_code, task_id, player_id, room
        )
        if success:
            await _broadcast_task_completed(room_code, task_id, player_id, from_player.name, newly_available)
    
    # Re-check locked tasks: the received item may satisfy ITEM prerequisites for the recipient
    game_state = game_state_manager.get_game_state(room_code)
    if game_state:
        recipient_item_ids = {inv_item.id for inv_item in to_player.inventory}
        item_unlocks = game_state.check_unlocks_with_items(recipient_item_ids)
        for new_task_id in item_unlocks:
            new_task = game_state.tasks.get(new_task_id)
            if new_task:
                for pid, p in room.players.items():
                    if p.role == new_task.assigned_role:
                        from app.models.websocket import TaskUnlockedMessage
                        unlocked_msg = TaskUnlockedMessage(
                            type="task_unlocked",
                            task=new_task.model_dump(mode='json')
                        )
                        await ws_manager.send_to_player(room_code, pid, unlocked_msg.model_dump(mode='json'))
                logger.info(f"🔓 Task {new_task_id} unlocked (ITEM prerequisite met after handoff to {to_player.name})")


async def handle_search_room(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle player searching their current room for items"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    game_state_manager = get_game_state_manager()
    
    room = room_manager.get_room(room_code)
    if not room or player_id not in room.players:
        return
    
    player = room.players[player_id]
    location = player.location
    
    # Get game state
    game_state = game_state_manager.get_game_state(room_code)
    if not game_state:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Game not started yet"
        })
        return
    
    # Normalize location to ID (try direct match first, then by normalized name)
    location_key = location
    if location not in game_state.items_by_location:
        # Try to find by location ID directly (location might be already an ID)
        # Or find location by normalized name
        for loc in game_state.locations:
            if loc.id == location or loc.name.lower() == location.lower():
                location_key = loc.id
                break
    
    # Get items at this location, filtered by unlock prerequisites
    all_items_here = game_state.items_by_location.get(location_key, [])
    visible_items = [item for item in all_items_here if game_state.check_item_visible(item)]

    # Further filter to items relevant to this player's role.
    # Items that appear in any search task's search_items are "claimed" by that task's role;
    # only the owning role (or tasks with no role claim) should be able to find them.
    # This prevents one player from accidentally picking up items intended for another role.
    role_claimed_items: Dict[str, str] = {}  # item_id -> assigned_role that needs it
    for task in game_state.tasks.values():
        if task.type.value == "search" and task.search_items:
            for item_id in task.search_items:
                role_claimed_items[item_id] = task.assigned_role

    player_role = room.players[player_id].role if player_id in room.players else None
    role_filtered = [
        item for item in visible_items
        if item.id not in role_claimed_items  # unclaimed — anyone can find it
        or role_claimed_items[item.id] == player_role  # claimed by this player's role
    ]

    # Send search results
    search_results = SearchResultsMessage(
        type="search_results",
        location=location,
        items=[item.model_dump(mode='json') for item in role_filtered]
    )
    await ws_manager.send_to_player(room_code, player_id, search_results.model_dump(mode='json'))

    logger.info(
        f"🔍 {player.name} ({player_role}) searched {location} - "
        f"found {len(role_filtered)}/{len(all_items_here)} items "
        f"(visible={len(visible_items)}, role-filtered={len(visible_items)-len(role_filtered)} hidden)"
    )


async def handle_pickup_item(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle player picking up an item"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    game_state_manager = get_game_state_manager()
    
    item_id = data.get("item_id")
    
    room = room_manager.get_room(room_code)
    if not room or player_id not in room.players:
        return
    
    player = room.players[player_id]
    location = player.location
    
    # Get game state
    game_state = game_state_manager.get_game_state(room_code)
    if not game_state:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Game not started yet"
        })
        return
    
    # Normalize location to ID (same logic as search)
    location_key = location
    if location not in game_state.items_by_location:
        for loc in game_state.locations:
            if loc.id == location or loc.name.lower() == location.lower():
                location_key = loc.id
                break
    
    # Find and remove item from location
    items_here = game_state.items_by_location.get(location_key, [])
    item = None
    for i, loc_item in enumerate(items_here):
        if loc_item.id == item_id:
            item = items_here.pop(i)
            break
    
    if not item:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Item not found at this location"
        })
        return
    
    # Add to player inventory
    # Import Item from room.py for player inventory
    from app.models.room import Item as PlayerItem
    player_item = PlayerItem(
        id=item.id,
        name=item.name,
        description=item.description
    )
    player.inventory.append(player_item)
    
    # Broadcast pickup
    pickup_msg = ItemPickedUpMessage(
        type="item_picked_up",
        player_id=player_id,
        player_name=player.name,
        item=item.model_dump(mode='json')
    )
    await ws_manager.broadcast_to_room(room_code, pickup_msg.model_dump(mode='json'))
    
    logger.info(f"📦 {player.name} picked up {item.name} from {location}")
    
    # Auto-complete any SEARCH tasks that now have all their items found
    completable_tasks = game_state_manager.check_search_completions(room_code, player_id, room)
    for task_id in completable_tasks:
        success, newly_available, error = game_state_manager.auto_complete_task(
            room_code, task_id, player_id, room
        )
        if success:
            await _broadcast_task_completed(room_code, task_id, player_id, player.name, newly_available)
    
    # Re-check all locked tasks: this item may satisfy ITEM prerequisites
    player_item_ids = {inv_item.id for inv_item in player.inventory}
    item_unlocks = game_state.check_unlocks_with_items(player_item_ids)
    for new_task_id in item_unlocks:
        new_task = game_state.tasks.get(new_task_id)
        if new_task:
            for pid, p in room.players.items():
                if p.role == new_task.assigned_role:
                    from app.models.websocket import TaskUnlockedMessage
                    unlocked_msg = TaskUnlockedMessage(
                        type="task_unlocked",
                        task=new_task.model_dump(mode='json')
                    )
                    await ws_manager.send_to_player(room_code, pid, unlocked_msg.model_dump(mode='json'))
            logger.info(f"🔓 Task {new_task_id} unlocked (ITEM prerequisite met by {player.name})")


async def handle_use_item(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle player attempting to use an item"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    
    item_id = data.get("item_id")
    
    room = room_manager.get_room(room_code)
    if not room or player_id not in room.players:
        return
    
    player = room.players[player_id]
    
    # Find item in player inventory
    item = None
    for inv_item in player.inventory:
        if inv_item.id == item_id:
            item = inv_item
            break
    
    if not item:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Item not in your inventory"
        })
        return
    
    # For now, items can't be used generically
    # This would be expanded to check for specific use cases
    # (e.g., keycard on door, food given to NPC, etc.)
    await ws_manager.send_to_player(room_code, player_id, {
        "type": "info",
        "message": f"{item.name} can't be used here. Try using it during a task or giving it to someone who needs it."
    })
    
    logger.info(f"🔧 {player.name} tried to use {item.name} at {player.location}")


async def handle_drop_item(room_code: str, player_id: str, data: Dict[str, Any]) -> None:
    """Handle player dropping an item in their current location"""
    ws_manager = get_ws_manager()
    room_manager = get_room_manager()
    game_state_manager = get_game_state_manager()
    
    item_id = data.get("item_id")
    
    room = room_manager.get_room(room_code)
    if not room or player_id not in room.players:
        return
    
    player = room.players[player_id]
    location = player.location
    
    # Get game state
    game_state = game_state_manager.get_game_state(room_code)
    if not game_state:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Game not started yet"
        })
        return
    
    # Find and remove item from player inventory
    item = None
    for i, inv_item in enumerate(player.inventory):
        if inv_item.id == item_id:
            item = player.inventory.pop(i)
            break
    
    if not item:
        await ws_manager.send_to_player(room_code, player_id, {
            "type": "error",
            "message": "Item not in your inventory"
        })
        return
    
    # Add item back to location
    from app.models.game_state import Item as GameItem
    dropped_item = GameItem(
        id=item.id,
        name=item.name,
        description=item.description,
        required_for=None,
        transferable=True
    )
    
    if location not in game_state.items_by_location:
        game_state.items_by_location[location] = []
    game_state.items_by_location[location].append(dropped_item)
    
    # Notify player
    await ws_manager.send_to_player(room_code, player_id, {
        "type": "item_dropped",
        "item_id": item.id,
        "item_name": item.name,
        "location": location
    })
    
    # Broadcast to team
    await ws_manager.broadcast_to_room(room_code, {
        "type": "info",
        "message": f"{player.name} dropped {item.name} in {location}"
    })
    
    logger.info(f"🗑️ {player.name} dropped {item.name} at {location}")
