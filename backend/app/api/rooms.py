"""
REST API endpoints for room management
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.room_manager import get_room_manager
from app.models.room import GameRoom, RoomStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


class CreateRoomRequest(BaseModel):
    """Request to create a new room"""
    host_name: str = Field(..., description="Host player name")


class CreateRoomResponse(BaseModel):
    """Response with new room details"""
    room_code: str = Field(..., description="Generated room code")
    player_id: str = Field(..., description="Host player ID")
    room: dict = Field(..., description="Room data")


class RoomInfoResponse(BaseModel):
    """Room information response"""
    room_code: str
    player_count: int
    status: str
    scenario: Optional[str]
    is_joinable: bool


@router.post("/create", response_model=CreateRoomResponse)
async def create_room(request: CreateRoomRequest):
    """
    Create a new game room
    
    The creator becomes the host and can start the game once players are ready.
    """
    room_manager = get_room_manager()
    
    try:
        room, player_id = room_manager.create_room(request.host_name)
        
        return CreateRoomResponse(
            room_code=room.room_code,
            player_id=player_id,
            room=room.model_dump()
        )
    
    except Exception as e:
        logger.error(f"Error creating room: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not create room")


@router.get("/{room_code}", response_model=RoomInfoResponse)
async def get_room_info(room_code: str):
    """
    Get information about a room
    
    Used to check if room exists before joining
    """
    room_manager = get_room_manager()
    
    room = room_manager.get_room(room_code)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {room_code} not found")
    
    return RoomInfoResponse(
        room_code=room.room_code,
        player_count=room.get_player_count(),
        status=room.status.value,
        scenario=room.scenario,
        is_joinable=room.status == RoomStatus.LOBBY and room.get_player_count() < 12
    )


@router.get("/", response_model=List[RoomInfoResponse])
async def list_rooms():
    """
    List all active rooms
    
    For development/debugging - will be removed in production
    """
    room_manager = get_room_manager()
    
    rooms = []
    for room_code, room in room_manager.rooms.items():
        if room.status != RoomStatus.ABANDONED:
            rooms.append(RoomInfoResponse(
                room_code=room.room_code,
                player_count=room.get_player_count(),
                status=room.status.value,
                scenario=room.scenario,
                is_joinable=room.status == RoomStatus.LOBBY and room.get_player_count() < 12
            ))
    
    return rooms
