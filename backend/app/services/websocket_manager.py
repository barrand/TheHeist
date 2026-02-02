"""
WebSocket Manager Service
Handles WebSocket connections and message broadcasting per room
"""

import logging
import json
from typing import Dict, Set, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for all rooms
    
    Responsibilities:
    - Track active WebSocket connections per room
    - Broadcast messages to all players in a room
    - Send targeted messages to specific players
    - Handle connection/disconnection events
    """
    
    def __init__(self):
        """Initialize WebSocket manager"""
        # room_code -> Dict[player_id -> WebSocket]
        self.connections: Dict[str, Dict[str, WebSocket]] = {}
        logger.info("WebSocketManager initialized")
    
    async def connect(self, room_code: str, player_id: str, websocket: WebSocket) -> None:
        """
        Register a new WebSocket connection
        
        Args:
            room_code: Room code
            player_id: Player ID
            websocket: WebSocket connection (already accepted)
        """
        # Don't accept here - it's already accepted in the websocket endpoint
        
        if room_code not in self.connections:
            self.connections[room_code] = {}
        
        self.connections[room_code][player_id] = websocket
        logger.info(f"🔌 Player {player_id} registered in room {room_code} connection pool")
    
    def disconnect(self, room_code: str, player_id: str) -> None:
        """
        Remove a WebSocket connection
        
        Args:
            room_code: Room code
            player_id: Player ID
        """
        if room_code in self.connections and player_id in self.connections[room_code]:
            del self.connections[room_code][player_id]
            logger.info(f"🔌 Player {player_id} disconnected from room {room_code}")
            
            # Clean up empty rooms
            if len(self.connections[room_code]) == 0:
                del self.connections[room_code]
                logger.info(f"🔌 Removed empty connection pool for room {room_code}")
    
    async def send_to_player(self, room_code: str, player_id: str, message: dict) -> bool:
        """
        Send message to a specific player
        
        Args:
            room_code: Room code
            player_id: Player ID
            message: Message dict to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if room_code not in self.connections:
            logger.warning(f"Room {room_code} has no connections")
            return False
        
        if player_id not in self.connections[room_code]:
            logger.warning(f"Player {player_id} not connected to room {room_code}")
            return False
        
        try:
            websocket = self.connections[room_code][player_id]
            await websocket.send_json(message)
            logger.debug(f"📤 Sent message to player {player_id} in room {room_code}: {message.get('type')}")
            return True
        except Exception as e:
            logger.error(f"Error sending to player {player_id}: {e}")
            self.disconnect(room_code, player_id)
            return False
    
    async def broadcast_to_room(self, room_code: str, message: dict, exclude_player: Optional[str] = None) -> int:
        """
        Broadcast message to all players in a room
        
        Args:
            room_code: Room code
            message: Message dict to send
            exclude_player: Optional player ID to exclude from broadcast
            
        Returns:
            Number of players message was sent to
        """
        if room_code not in self.connections:
            logger.warning(f"Room {room_code} has no connections")
            return 0
        
        all_players = list(self.connections[room_code].keys())
        logger.info(f"📢 Broadcasting {message.get('type')} to room {room_code} with {len(all_players)} players: {all_players}")
        if exclude_player:
            logger.info(f"   Excluding player: {exclude_player}")
        
        sent_count = 0
        failed_players = []
        
        for player_id, websocket in list(self.connections[room_code].items()):
            if exclude_player and player_id == exclude_player:
                logger.info(f"   ⏭️  Skipping excluded player {player_id}")
                continue
            
            try:
                await websocket.send_json(message)
                logger.info(f"   ✅ Sent to player {player_id}")
                sent_count += 1
            except Exception as e:
                logger.error(f"   ❌ Error broadcasting to player {player_id}: {e}")
                failed_players.append(player_id)
        
        # Clean up failed connections
        for player_id in failed_players:
            self.disconnect(room_code, player_id)
        
        logger.info(f"📢 Broadcast complete: {sent_count} players received the message")
        return sent_count
    
    def get_connected_players(self, room_code: str) -> Set[str]:
        """
        Get set of connected player IDs for a room
        
        Args:
            room_code: Room code
            
        Returns:
            Set of player IDs
        """
        if room_code not in self.connections:
            return set()
        return set(self.connections[room_code].keys())
    
    def is_player_connected(self, room_code: str, player_id: str) -> bool:
        """Check if a player is connected via WebSocket"""
        return room_code in self.connections and player_id in self.connections[room_code]
    
    def get_room_count(self) -> int:
        """Get number of rooms with active connections"""
        return len(self.connections)
    
    def get_total_connections(self) -> int:
        """Get total number of active WebSocket connections"""
        return sum(len(players) for players in self.connections.values())


# Global WebSocket manager instance
_ws_manager: Optional[WebSocketManager] = None


def get_ws_manager() -> WebSocketManager:
    """Get or create global WebSocketManager instance"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
