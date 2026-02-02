"""
Data models for game rooms and players
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime


class RoomStatus(str, Enum):
    """Current status of a game room"""
    LOBBY = "lobby"              # Players joining and selecting roles
    IN_PROGRESS = "in_progress"  # Game actively being played
    COMPLETED = "completed"      # Game finished
    ABANDONED = "abandoned"      # All players disconnected


class Item(BaseModel):
    """An item in a player's inventory"""
    id: str = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="What the item is")
    
    
class Player(BaseModel):
    """A player in a game room"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    id: str = Field(..., description="Unique player identifier (UUID)")
    name: str = Field(..., description="Player display name")
    role: Optional[str] = Field(None, description="Selected role (mastermind, hacker, etc.)")
    connected: bool = Field(default=True, description="Is player currently connected")
    location: str = Field(default="Safe House", description="Current location in game")
    inventory: List[Item] = Field(default_factory=list, description="Items player is carrying")
    joined_at: datetime = Field(default_factory=datetime.utcnow, description="When player joined")


class GameRoom(BaseModel):
    """A multiplayer game room"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    room_code: str = Field(..., description="4-character room code (e.g., '4S2X')")
    host_id: str = Field(..., description="Player ID of room host (first to join)")
    players: Dict[str, Player] = Field(default_factory=dict, description="player_id -> Player")
    scenario: Optional[str] = Field(None, description="Selected scenario (e.g., 'museum_gala_vault')")
    status: RoomStatus = Field(default=RoomStatus.LOBBY, description="Current room status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Room creation time")
    game_started_at: Optional[datetime] = Field(None, description="When game actually started")
    
    def get_player_count(self) -> int:
        """Get number of players in room"""
        return len(self.players)
    
    def is_host(self, player_id: str) -> bool:
        """Check if player is the host"""
        return player_id == self.host_id
    
    def get_connected_players(self) -> List[Player]:
        """Get list of currently connected players"""
        return [p for p in self.players.values() if p.connected]
    
    def get_selected_roles(self) -> List[str]:
        """Get list of roles that have been selected"""
        return [p.role for p in self.players.values() if p.role is not None]
    
    def all_roles_selected(self) -> bool:
        """Check if all players have selected roles"""
        return all(p.role is not None for p in self.players.values())
