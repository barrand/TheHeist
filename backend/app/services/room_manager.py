"""
Room Manager Service
Handles room creation, player joining, and room lifecycle management
"""

import logging
import random
import string
import uuid
from typing import Dict, Optional, List
from datetime import datetime

from app.models.room import GameRoom, Player, RoomStatus

logger = logging.getLogger(__name__)


class RoomManager:
    """
    Manages all active game rooms
    
    Responsibilities:
    - Generate unique room codes
    - Create new rooms
    - Add/remove players from rooms
    - Track active rooms
    - Clean up abandoned rooms
    """
    
    def __init__(self):
        """Initialize room manager with in-memory storage"""
        self.rooms: Dict[str, GameRoom] = {}  # room_code -> GameRoom
        logger.info("RoomManager initialized")
    
    def generate_room_code(self) -> str:
        """
        Generate a unique 4-character room code
        Format: XNXN where X=letter, N=number (e.g., "4S2X" or "A1B2")
        
        Returns:
            Unique room code
        """
        max_attempts = 100
        for _ in range(max_attempts):
            # Generate code: digit-letter-digit-letter
            code = ''.join([
                random.choice(string.digits),
                random.choice(string.ascii_uppercase),
                random.choice(string.digits),
                random.choice(string.ascii_uppercase),
            ])
            
            if code not in self.rooms:
                return code
        
        # Fallback to random alphanumeric if pattern exhausted
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            if code not in self.rooms:
                return code
    
    def create_room(self, host_name: str) -> tuple[GameRoom, str]:
        """
        Create a new game room
        
        Args:
            host_name: Display name of the host player
            
        Returns:
            Tuple of (GameRoom, player_id)
        """
        room_code = self.generate_room_code()
        player_id = str(uuid.uuid4())
        
        # Create host player
        host = Player(
            id=player_id,
            name=host_name,
            role=None,
            connected=True
        )
        
        # Create room
        room = GameRoom(
            room_code=room_code,
            host_id=player_id,
            players={player_id: host},
            status=RoomStatus.LOBBY
        )
        
        self.rooms[room_code] = room
        logger.info(f"✨ Created room {room_code} with host {host_name} ({player_id})")
        
        return room, player_id
    
    def get_room(self, room_code: str) -> Optional[GameRoom]:
        """Get room by code"""
        return self.rooms.get(room_code)
    
    def join_room(self, room_code: str, player_name: str) -> Optional[tuple[GameRoom, str]]:
        """
        Add player to existing room
        
        Args:
            room_code: Code of room to join
            player_name: Player's display name
            
        Returns:
            Tuple of (GameRoom, player_id) if successful, None if room doesn't exist
        """
        room = self.get_room(room_code)
        if not room:
            logger.warning(f"❌ Room {room_code} not found")
            return None
        
        if room.status != RoomStatus.LOBBY:
            logger.warning(f"❌ Room {room_code} is not in lobby (status: {room.status})")
            return None
        
        # Check player limit (3-12 players)
        if len(room.players) >= 12:
            logger.warning(f"❌ Room {room_code} is full (12 players)")
            return None
        
        # Create player
        player_id = str(uuid.uuid4())
        player = Player(
            id=player_id,
            name=player_name,
            role=None,
            connected=True
        )
        
        room.players[player_id] = player
        logger.info(f"✅ Player {player_name} ({player_id}) joined room {room_code}")
        
        return room, player_id
    
    def remove_player(self, room_code: str, player_id: str) -> bool:
        """
        Remove player from room (disconnect/leave)
        
        Args:
            room_code: Room code
            player_id: Player to remove
            
        Returns:
            True if player was removed, False otherwise
        """
        room = self.get_room(room_code)
        if not room or player_id not in room.players:
            return False
        
        player_name = room.players[player_id].name
        del room.players[player_id]
        logger.info(f"👋 Player {player_name} ({player_id}) left room {room_code}")
        
        # If no players left, mark room as abandoned
        if len(room.players) == 0:
            room.status = RoomStatus.ABANDONED
            logger.info(f"🏚️  Room {room_code} is now abandoned")
        
        # If host left, assign new host
        elif room.host_id == player_id:
            new_host_id = next(iter(room.players.keys()))
            room.host_id = new_host_id
            logger.info(f"👑 New host for room {room_code}: {room.players[new_host_id].name}")
        
        return True
    
    def set_player_role(self, room_code: str, player_id: str, role: str) -> bool:
        """
        Set a player's role in lobby
        
        Args:
            room_code: Room code
            player_id: Player ID
            role: Role name (e.g., "mastermind", "hacker")
            
        Returns:
            True if successful, False otherwise
        """
        room = self.get_room(room_code)
        if not room or player_id not in room.players:
            return False
        
        if room.status != RoomStatus.LOBBY:
            logger.warning(f"❌ Cannot change role - room {room_code} not in lobby")
            return False
        
        # Check if role already taken
        for pid, player in room.players.items():
            if pid != player_id and player.role == role:
                logger.warning(f"❌ Role {role} already taken in room {room_code}")
                return False
        
        room.players[player_id].role = role
        logger.info(f"✅ Player {room.players[player_id].name} selected role: {role}")
        return True
    
    def start_game(self, room_code: str, player_id: str, scenario: str) -> bool:
        """
        Start the game (host only)
        
        Args:
            room_code: Room code
            player_id: Player attempting to start (must be host)
            scenario: Scenario ID to play
            
        Returns:
            True if game started, False otherwise
        """
        room = self.get_room(room_code)
        if not room:
            return False
        
        # Check if player is host
        if not room.is_host(player_id):
            logger.warning(f"❌ Player {player_id} is not host of room {room_code}")
            return False
        
        # Check if in lobby
        if room.status != RoomStatus.LOBBY:
            logger.warning(f"❌ Room {room_code} not in lobby status")
            return False
        
        # Check player count (3-12)
        player_count = room.get_player_count()
        if player_count < 3:
            logger.warning(f"❌ Room {room_code} needs at least 3 players (has {player_count})")
            return False
        
        # Check if all players selected roles
        if not room.all_roles_selected():
            logger.warning(f"❌ Not all players in room {room_code} have selected roles")
            return False
        
        # Start game
        room.scenario = scenario
        room.status = RoomStatus.IN_PROGRESS
        room.game_started_at = datetime.utcnow()
        
        logger.info(f"🎮 Game started in room {room_code} - scenario: {scenario}, players: {player_count}")
        return True
    
    def end_game(self, room_code: str, result: str) -> bool:
        """
        End the game
        
        Args:
            room_code: Room code
            result: "success" or "failure"
            
        Returns:
            True if ended, False otherwise
        """
        room = self.get_room(room_code)
        if not room:
            return False
        
        if room.status != RoomStatus.IN_PROGRESS:
            return False
        
        room.status = RoomStatus.COMPLETED
        logger.info(f"🏁 Game ended in room {room_code} - result: {result}")
        return True
    
    def cleanup_abandoned_rooms(self, max_age_minutes: int = 60) -> int:
        """
        Remove abandoned rooms older than threshold
        
        Args:
            max_age_minutes: Maximum age for abandoned rooms
            
        Returns:
            Number of rooms cleaned up
        """
        now = datetime.utcnow()
        to_remove = []
        
        for room_code, room in self.rooms.items():
            if room.status == RoomStatus.ABANDONED:
                age_minutes = (now - room.created_at).total_seconds() / 60
                if age_minutes > max_age_minutes:
                    to_remove.append(room_code)
        
        for room_code in to_remove:
            del self.rooms[room_code]
            logger.info(f"🧹 Cleaned up abandoned room {room_code}")
        
        return len(to_remove)
    
    def get_active_room_count(self) -> int:
        """Get number of active (non-abandoned) rooms"""
        return sum(1 for room in self.rooms.values() if room.status != RoomStatus.ABANDONED)


# Global room manager instance
_room_manager: Optional[RoomManager] = None


def get_room_manager() -> RoomManager:
    """Get or create global RoomManager instance"""
    global _room_manager
    if _room_manager is None:
        _room_manager = RoomManager()
    return _room_manager
