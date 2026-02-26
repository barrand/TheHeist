"""
Bot Player for E2E Testing

Simulates a player connecting to the game via WebSocket and performing actions.
Each bot represents one player/role in a scenario.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List, Set, Any
from dataclasses import dataclass, field
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)


@dataclass
class BotPlayerState:
    """Local state tracked by the bot"""
    player_id: Optional[str] = None
    player_name: str = ""
    role: str = ""
    difficulty: str = "medium"
    
    current_location: str = ""
    inventory: List[Dict] = field(default_factory=list)
    
    available_tasks: Dict[str, Dict] = field(default_factory=dict)
    completed_tasks: Set[str] = field(default_factory=set)
    
    achieved_outcomes: Set[str] = field(default_factory=set)
    
    npcs: List[Dict] = field(default_factory=list)
    locations: List[Dict] = field(default_factory=list)
    
    game_started: bool = False
    is_host: bool = False


class BotPlayer:
    """
    A bot player that connects to the game via WebSocket and performs actions.
    
    Can:
    - Join room
    - Select role
    - Start game (if host)
    - Move to locations
    - Search for items
    - Pick up items
    - Complete tasks
    - Talk to NPCs
    - Handoff items to other players
    """
    
    def __init__(
        self, 
        player_name: str, 
        role: str,
        difficulty: str = "medium",
        backend_url: str = "ws://localhost:8000"
    ):
        self.player_name = player_name
        self.role = role
        self.difficulty = difficulty
        self.backend_url = backend_url
        
        self.state = BotPlayerState(
            player_name=player_name,
            role=role,
            difficulty=difficulty
        )
        
        self.ws: Optional[WebSocketClientProtocol] = None
        self.room_code: Optional[str] = None
        
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        
        logger.info(f"Bot {player_name} ({role}) initialized")
    
    async def connect(self, room_code: str) -> bool:
        """
        Connect to game room via WebSocket
        
        Returns:
            True if successfully connected and joined
        """
        self.room_code = room_code
        ws_url = f"{self.backend_url}/ws/{room_code}"
        
        try:
            self.ws = await websockets.connect(ws_url)
            logger.info(f"Bot {self.player_name} connected to {ws_url}")
            
            # Start message receiver
            self._running = True
            asyncio.create_task(self._message_receiver())
            
            # Send join message
            await self._send({
                "type": "join_room",
                "room_code": room_code,
                "player_name": self.player_name
            })
            
            # Wait for room_state message
            msg = await self._wait_for_message("room_state", timeout=5)
            if msg:
                self.state.player_id = msg.get("your_player_id")
                self.state.is_host = msg.get("is_host", False)
                logger.info(f"Bot {self.player_name} joined as {self.state.player_id}, host={self.state.is_host}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Bot {self.player_name} failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        self._running = False
        if self.ws:
            await self.ws.close()
            logger.info(f"Bot {self.player_name} disconnected")
    
    async def select_role(self) -> bool:
        """Select role in lobby"""
        if not self.ws:
            return False
        
        await self._send({
            "type": "select_role",
            "role": self.role,
            "difficulty": self.difficulty
        })
        
        # Wait for confirmation
        msg = await self._wait_for_message("role_selected", timeout=3)
        return msg is not None
    
    async def start_game(self, scenario: str) -> bool:
        """
        Start the game (host only, or E2E testing bypass)
        
        Args:
            scenario: Scenario ID to play
        """
        # For E2E testing, skip host check (backend will validate)
        if not self.state.is_host:
            logger.warning(f"Bot {self.player_name} is not marked as host, but attempting to start game for E2E testing")
        
        await self._send({
            "type": "start_game",
            "scenario": scenario
        })
        
        # Wait for game_started
        msg = await self._wait_for_message("game_started", timeout=5)
        if msg:
            self.state.game_started = True
            self.state.available_tasks = {
                task["id"]: task for task in msg.get("your_tasks", [])
            }
            self.state.npcs = msg.get("npcs", [])
            self.state.locations = msg.get("locations", [])
            logger.info(f"Bot {self.player_name} received {len(self.state.available_tasks)} tasks")
            return True
        
        return False
    
    async def move_to_location(self, location: str) -> bool:
        """Move to a different location"""
        await self._send({
            "type": "move_location",
            "location": location
        })
        
        # Wait for player_moved broadcast
        msg = await self._wait_for_message("player_moved", timeout=3)
        if msg and msg.get("player_id") == self.state.player_id:
            self.state.current_location = location
            logger.info(f"Bot {self.player_name} moved to {location}")
            return True
        
        return False
    
    async def search_location(self) -> List[Dict]:
        """Search current location for items"""
        await self._send({
            "type": "search_room"
        })
        
        # Wait for search_results
        msg = await self._wait_for_message("search_results", timeout=3)
        if msg:
            items = msg.get("items", [])
            logger.info(f"Bot {self.player_name} found {len(items)} items at {self.state.current_location}")
            return items
        
        return []
    
    async def pickup_item(self, item_id: str) -> bool:
        """Pick up an item from current location"""
        await self._send({
            "type": "pickup_item",
            "item_id": item_id
        })
        
        # Wait for item_picked_up broadcast
        msg = await self._wait_for_message("item_picked_up", timeout=3)
        if msg and msg.get("player_id") == self.state.player_id:
            item = msg.get("item")
            self.state.inventory.append(item)
            logger.info(f"Bot {self.player_name} picked up {item.get('name', item_id)}")
            return True
        
        return False
    
    async def handoff_item(self, item_id: str, to_player_id: str) -> bool:
        """Hand off item to another player"""
        await self._send({
            "type": "handoff_item",
            "item_id": item_id,
            "to_player_id": to_player_id
        })
        
        # Wait for item_transferred broadcast
        msg = await self._wait_for_message("item_transferred", timeout=3)
        if msg and msg.get("from_player_id") == self.state.player_id:
            # Remove from inventory
            self.state.inventory = [i for i in self.state.inventory if i["id"] != item_id]
            logger.info(f"Bot {self.player_name} handed off {item_id} to {to_player_id}")
            return True
        
        return False
    
    async def complete_task(self, task_id: str) -> bool:
        """
        Mark a task as complete
        
        For minigame tasks, this simulates successful minigame completion.
        For other task types, completion happens via other methods.
        """
        await self._send({
            "type": "complete_task",
            "task_id": task_id
        })
        
        # Wait for task_completed broadcast
        msg = await self._wait_for_message("task_completed", timeout=5)
        if msg and msg.get("task_id") == task_id:
            self.state.completed_tasks.add(task_id)
            
            # Track achieved outcomes
            for outcome in msg.get("achieved_outcomes", []):
                self.state.achieved_outcomes.add(outcome)
            
            # Remove from available tasks
            if task_id in self.state.available_tasks:
                del self.state.available_tasks[task_id]
            
            logger.info(f"Bot {self.player_name} completed task {task_id}")
            return True
        
        return False
    
    async def talk_to_npc(self, task_id: str, npc_id: str, message: str) -> Optional[Dict]:
        """
        Send a message to an NPC
        
        Returns:
            NPC response dict or None
        """
        await self._send({
            "type": "npc_message",
            "task_id": task_id,
            "npc_id": npc_id,
            "message": message
        })
        
        # Wait for npc_response
        msg = await self._wait_for_message("npc_response", timeout=10)
        if msg and msg.get("task_id") == task_id:
            logger.info(f"Bot {self.player_name} got NPC response: {msg.get('text', '')[:50]}...")
            return msg
        
        return None
    
    def has_available_tasks(self) -> bool:
        """Check if bot has any tasks it can work on"""
        return len(self.state.available_tasks) > 0
    
    def get_available_tasks(self) -> List[Dict]:
        """Get list of available tasks"""
        return list(self.state.available_tasks.values())
    
    def has_item(self, item_id: str) -> bool:
        """Check if bot has specific item in inventory"""
        return any(item["id"] == item_id for item in self.state.inventory)
    
    # ==========================================
    # Internal Methods
    # ==========================================
    
    async def _send(self, message: Dict):
        """Send message via WebSocket"""
        if not self.ws:
            raise RuntimeError("Not connected")
        
        await self.ws.send(json.dumps(message))
    
    async def _message_receiver(self):
        """Background task that receives and queues messages"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self._message_queue.put(data)
                
                # Handle messages that update state
                await self._handle_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Bot {self.player_name} connection closed")
        except Exception as e:
            logger.error(f"Bot {self.player_name} message receiver error: {e}")
    
    async def _handle_message(self, msg: Dict):
        """Process messages that update bot state"""
        msg_type = msg.get("type")
        
        if msg_type == "task_unlocked":
            task = msg.get("task")
            if task:
                self.state.available_tasks[task["id"]] = task
                logger.info(f"Bot {self.player_name} unlocked task {task['id']}")
        
        elif msg_type == "task_completed":
            # Track outcomes achieved by any player
            for outcome in msg.get("achieved_outcomes", []):
                self.state.achieved_outcomes.add(outcome)
        
        elif msg_type == "item_picked_up":
            # Track if this bot picked up item (already handled in pickup_item)
            pass
        
        elif msg_type == "game_ended":
            logger.info(f"Bot {self.player_name} saw game end: {msg.get('result')}")
    
    async def _wait_for_message(self, message_type: str, timeout: float = 10) -> Optional[Dict]:
        """
        Wait for a specific message type
        
        Returns:
            Message dict or None if timeout
        """
        try:
            deadline = asyncio.get_event_loop().time() + timeout
            
            while asyncio.get_event_loop().time() < deadline:
                try:
                    msg = await asyncio.wait_for(
                        self._message_queue.get(),
                        timeout=deadline - asyncio.get_event_loop().time()
                    )
                    
                    if msg.get("type") == message_type:
                        return msg
                    
                    # Not the message we want, put it back
                    await self._message_queue.put(msg)
                    await asyncio.sleep(0.1)
                    
                except asyncio.TimeoutError:
                    break
            
            return None
            
        except Exception as e:
            logger.error(f"Error waiting for message {message_type}: {e}")
            return None
