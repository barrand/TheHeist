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
    room_code: str = ""
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
    game_ended: bool = False
    game_result: Optional[str] = None
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
        self.state.room_code = room_code  # Store in state for NPC conversations
        ws_url = f"{self.backend_url}/ws/{room_code}"
        
        try:
            self.ws = await websockets.connect(ws_url)
            logger.info(f"Bot {self.player_name} connected to {ws_url}")
            
            # Start message receiver
            self._running = True
            asyncio.create_task(self._message_receiver())
            
            # Send join message
            join_msg = {
                "type": "join_room",
                "room_code": room_code,
                "player_name": self.player_name
            }
            logger.debug(f"Bot {self.player_name} sending join_room: {join_msg}")
            await self._send(join_msg)
            
            # Wait for room_state message
            logger.debug(f"Bot {self.player_name} waiting for room_state...")
            msg = await self._wait_for_message("room_state", timeout=5)
            if msg:
                self.state.player_id = msg.get("your_player_id")
                self.state.is_host = msg.get("is_host", False)
                logger.info(f"Bot {self.player_name} joined as {self.state.player_id}, host={self.state.is_host}")
                return True
            
            logger.error(f"Bot {self.player_name} timed out waiting for room_state")
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
        Start the game (host only)
        
        Args:
            scenario: Scenario ID to play
        """
        if not self.state.is_host:
            logger.warning(f"Bot {self.player_name} is not host, cannot start game")
            return False
        
        await self._send({
            "type": "start_game",
            "scenario": scenario,
            "skip_images": True  # Skip image generation for E2E testing
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
            starting_loc = msg.get("starting_location", "")
            self.state.location = starting_loc
            self.state.current_location = starting_loc
            logger.info(f"Bot {self.player_name} received {len(self.state.available_tasks)} tasks at {starting_loc}")
            return True
        
        return False
    
    async def move_to_location(self, location: str) -> bool:
        """Move to a different location"""
        await self._send({
            "type": "move_location",
            "location": location
        })
        
        # For E2E testing, assume move succeeds immediately (backend bypasses validation for bots)
        # This avoids message queue congestion from multiple player_moved broadcasts
        self.state.current_location = location
        self.state.location = location
        logger.info(f"Bot {self.player_name} moved to {location}")
        await asyncio.sleep(0.1)  # Small delay for backend processing
        return True
    
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
        
        For E2E testing, assumes success to avoid message queue congestion.
        The backend broadcasts task_completed which _handle_message processes.
        """
        await self._send({
            "type": "complete_task",
            "task_id": task_id
        })
        
        # For E2E testing, assume success immediately
        # The task_completed broadcast will be processed by _handle_message
        await asyncio.sleep(0.2)  # Small delay for backend processing
        
        # Mark as completed optimistically
        self.state.completed_tasks.add(task_id)
        if task_id in self.state.available_tasks:
            del self.state.available_tasks[task_id]
        
        logger.info(f"Bot {self.player_name} completed task {task_id} (E2E instant mode)")
        return True
    
    async def start_npc_conversation(self, task_id: str, npc_id: str, cover_id: str, target_outcomes: list) -> Optional[Dict]:
        """
        Start NPC conversation by choosing a cover story
        
        Returns:
            {greeting, quick_responses, suspicion} or None
        """
        import aiohttp
        
        url = f"{self.backend_url}/api/npc/start-conversation"
        payload = {
            "npc_id": npc_id,
            "cover_id": cover_id,
            "room_code": self.state.room_code,
            "player_id": self.state.player_id,
            "target_outcomes": target_outcomes
        }
        
        # Exponential backoff for rate limiting
        max_retries = 5
        base_delay = 2
        max_delay = 60
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"Bot {self.player_name} started conversation with {npc_id} (suspicion={data.get('suspicion', 0)})")
                            return data
                        elif response.status == 429:
                            # Rate limited - exponential backoff
                            if attempt < max_retries - 1:
                                delay = min(base_delay * (2 ** attempt), max_delay)
                                logger.warning(f"Bot {self.player_name} rate limited (429), retrying in {delay}s (attempt {attempt+1}/{max_retries})")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"Bot {self.player_name} rate limited after {max_retries} attempts")
                                return None
                        else:
                            logger.error(f"Bot {self.player_name} failed to start conversation: {response.status}")
                            return None
            except Exception as e:
                logger.error(f"Bot {self.player_name} error starting conversation: {e}")
                if attempt < max_retries - 1:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    return None
        
        return None
    
    async def send_npc_choice(self, npc_id: str, response_index: int) -> Optional[Dict]:
        """
        Send a quick response choice to NPC
        
        Returns:
            {npc_response, outcomes, suspicion, quick_responses, conversation_failed} or None
        """
        import aiohttp
        
        url = f"{self.backend_url}/api/npc/chat"
        payload = {
            "response_index": response_index,
            "room_code": self.state.room_code,
            "player_id": self.state.player_id,
            "npc_id": npc_id
        }
        
        # Exponential backoff for rate limiting
        max_retries = 5
        base_delay = 2
        max_delay = 60
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"Bot {self.player_name} sent choice to {npc_id} (suspicion={data.get('suspicion', 0)})")
                            
                            # Track completed tasks
                            for task_id in data.get('completed_tasks', []):
                                self.state.completed_tasks.add(task_id)
                                if task_id in self.state.available_tasks:
                                    del self.state.available_tasks[task_id]
                            
                            return data
                        elif response.status == 429:
                            # Rate limited - exponential backoff
                            if attempt < max_retries - 1:
                                delay = min(base_delay * (2 ** attempt), max_delay)
                                logger.warning(f"Bot {self.player_name} rate limited (429), retrying in {delay}s (attempt {attempt+1}/{max_retries})")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"Bot {self.player_name} rate limited after {max_retries} attempts")
                                return None
                        else:
                            logger.error(f"Bot {self.player_name} failed to send choice: {response.status}")
                            return None
            except Exception as e:
                logger.error(f"Bot {self.player_name} error sending choice: {e}")
                if attempt < max_retries - 1:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    return None
        
        return None
    
    def has_available_tasks(self) -> bool:
        """Check if bot has any tasks it can work on"""
        return len(self.state.available_tasks) > 0
    
    def get_available_tasks(self) -> List[Dict]:
        """
        Get list of available tasks, filtered for client-side intelligence
        
        Filters out:
        - SEARCH tasks where bot already has all required items
        """
        tasks = list(self.state.available_tasks.values())
        filtered_tasks = []
        
        for task in tasks:
            # Skip SEARCH tasks if we already have all the items
            if task.get("type") == "search" and task.get("search_items"):
                required_items = task.get("search_items", [])
                inventory_ids = {item.get("id") for item in self.state.inventory}
                
                # Check if we have all required items
                has_all_items = all(item_id in inventory_ids for item_id in required_items)
                
                if has_all_items:
                    logger.debug(f"🧠 Smart filter: Skipping {task.get('id')} - already have all items: {required_items}")
                    continue  # Skip this task - we already have what we need
            
            filtered_tasks.append(task)
        
        return filtered_tasks
    
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
            while self._running:
                try:
                    message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                    data = json.loads(message)
                    await self._message_queue.put(data)
                    
                    # Handle messages that update state
                    await self._handle_message(data)
                    
                except asyncio.TimeoutError:
                    continue  # No message received, continue loop
                except json.JSONDecodeError as e:
                    logger.error(f"Bot {self.player_name} JSON decode error: {e}")
                    continue
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Bot {self.player_name} connection closed")
        except Exception as e:
            logger.error(f"Bot {self.player_name} message receiver error: {e}", exc_info=True)
    
    async def _handle_message(self, msg: Dict):
        """Process messages that update bot state"""
        msg_type = msg.get("type")
        
        if msg_type == "error":
            # Log backend error responses
            error_msg = msg.get("message", "Unknown error")
            logger.error(f"❌ Backend error for {self.player_name}: {error_msg}")
        
        elif msg_type == "game_started":
            # Non-host bots receive game_started via this path
            self.state.game_started = True
            self.state.available_tasks = {
                task["id"]: task for task in msg.get("your_tasks", [])
            }
            self.state.npcs = msg.get("npcs", [])
            self.state.locations = msg.get("locations", [])
            starting_loc = msg.get("starting_location", "")
            self.state.location = starting_loc
            self.state.current_location = starting_loc
            logger.info(f"Bot {self.player_name} received {len(self.state.available_tasks)} tasks at {starting_loc}")
        
        elif msg_type == "task_unlocked":
            task = msg.get("task")
            if task:
                self.state.available_tasks[task["id"]] = task
                logger.info(f"Bot {self.player_name} unlocked task {task['id']}")
        
        elif msg_type == "task_completed":
            # Track outcomes achieved by any player
            for outcome in msg.get("achieved_outcomes", []):
                self.state.achieved_outcomes.add(outcome)
            
            # Track completed tasks and remove from available tasks
            completed_task_id = msg.get("task_id")
            if completed_task_id:
                # Only add to completed_tasks if this task was assigned to this bot
                # (it was in available_tasks at some point)
                if completed_task_id in self.state.available_tasks:
                    self.state.completed_tasks.add(completed_task_id)
                    del self.state.available_tasks[completed_task_id]
                    logger.debug(f"Bot {self.player_name} marked own task {completed_task_id} as completed (via broadcast)")
                else:
                    # Task was completed by another role - just track the outcomes
                    logger.debug(f"Bot {self.player_name} saw other role complete task {completed_task_id}")
        
        elif msg_type == "item_picked_up":
            # Track if this bot picked up item (already handled in pickup_item)
            pass
        
        elif msg_type == "game_ended":
            self.state.game_ended = True
            self.state.game_result = msg.get("result", "unknown")
            logger.info(f"Bot {self.player_name} saw game end: {self.state.game_result}")
    
    async def _wait_for_message(self, message_type: str, timeout: float = 10) -> Optional[Dict]:
        """
        Wait for a specific message type
        
        Returns:
            Message dict or None if timeout
        """
        try:
            deadline = asyncio.get_event_loop().time() + timeout
            discarded_messages = []
            
            while asyncio.get_event_loop().time() < deadline:
                try:
                    msg = await asyncio.wait_for(
                        self._message_queue.get(),
                        timeout=deadline - asyncio.get_event_loop().time()
                    )
                    
                    if msg.get("type") == message_type:
                        # Put discarded messages back before returning
                        for discarded in discarded_messages:
                            await self._message_queue.put(discarded)
                        return msg
                    
                    # Discard this message (don't put it back to avoid infinite loop)
                    discarded_messages.append(msg)
                    
                except asyncio.TimeoutError:
                    break
            
            # Timeout - put discarded messages back
            for discarded in discarded_messages:
                await self._message_queue.put(discarded)
            
            logger.debug(f"Bot {self.player_name} timed out waiting for '{message_type}' after {timeout}s (discarded {len(discarded_messages)} other messages)")
            return None
            
        except Exception as e:
            logger.error(f"Error waiting for message {message_type}: {e}")
            return None
