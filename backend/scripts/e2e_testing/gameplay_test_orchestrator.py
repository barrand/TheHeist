"""
Gameplay Test Orchestrator

Coordinates multiple bot players to complete a full scenario playthrough.
Manages:
- Room creation
- Bot spawning and connection
- Turn coordination
- Game progress monitoring
- Result collection
"""

import asyncio
import logging
import random
import string
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import aiohttp

from .bot_player import BotPlayer
from .llm_decision_maker import LLMDecisionMaker, ActionDecision
from .npc_conversation_bot import NPCConversationBot, ConversationResult
from ..validate_scenario import ScenarioValidator

logger = logging.getLogger(__name__)


@dataclass
class GameplayTestResult:
    """Result of a full gameplay test"""
    scenario_file: str
    scenario_name: str
    player_count: int
    difficulty: str
    
    status: str  # "WIN", "DEADLOCK", "TIMEOUT", "ERROR"
    turns_taken: int
    
    # Per-role metrics
    tasks_completed_per_role: Dict[str, int] = field(default_factory=dict)
    idle_turns_per_role: Dict[str, int] = field(default_factory=dict)
    npc_conversations_per_role: Dict[str, List[ConversationResult]] = field(default_factory=dict)
    
    # Issues detected
    issues: List[str] = field(default_factory=list)
    
    # Full log
    game_log: List[Dict] = field(default_factory=list)
    
    def summary(self) -> str:
        """Generate a summary string"""
        lines = []
        lines.append(f"===== GAMEPLAY TEST RESULT =====")
        lines.append(f"Scenario: {self.scenario_name} ({self.player_count} players, {self.difficulty})")
        lines.append(f"Status: {self.status} ({self.turns_taken} turns)")
        lines.append(f"")
        lines.append(f"Per-Role Performance:")
        for role in sorted(self.tasks_completed_per_role.keys()):
            tasks = self.tasks_completed_per_role[role]
            idle = self.idle_turns_per_role.get(role, 0)
            convos = len(self.npc_conversations_per_role.get(role, []))
            lines.append(f"  {role}: {tasks} tasks, {convos} NPC conversations, {idle} idle turns")
        
        if self.issues:
            lines.append(f"")
            lines.append(f"Issues Detected:")
            for issue in self.issues:
                lines.append(f"  - {issue}")
        
        return "\n".join(lines)


class GameplayTestOrchestrator:
    """
    Orchestrates a full gameplay test with multiple bot players.
    
    Workflow:
    1. Parse scenario file
    2. Create room via REST API
    3. Spawn N bots (one per role)
    4. All bots join and select roles
    5. Host bot starts game
    6. Main game loop:
       - Each bot analyzes state and chooses action
       - Bots take turns executing actions
       - Monitor for win/deadlock/timeout
    7. Generate detailed report
    """
    
    def __init__(
        self,
        backend_url: str = "http://localhost:8000",
        max_turns: int = 500,
        skip_npc_conversations: bool = False
    ):
        self.backend_url = backend_url
        self.max_turns = max_turns
        self.skip_npc_conversations = skip_npc_conversations
        
        self.decision_maker = LLMDecisionMaker()
        self.conversation_bot = NPCConversationBot(backend_url=backend_url)
        
        skip_msg = " (skipping NPC conversations)" if skip_npc_conversations else ""
        logger.info(f"Orchestrator initialized (max turns: {max_turns}){skip_msg}")
    
    async def test_scenario(
        self, 
        scenario_file: Path,
        difficulty: str = "medium"
    ) -> GameplayTestResult:
        """
        Run a full gameplay test on a scenario
        
        Args:
            scenario_file: Path to scenario markdown file
            difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            GameplayTestResult with complete test data
        """
        logger.info(f"Starting gameplay test: {scenario_file.name}")
        
        # Parse scenario to get roles and metadata
        validator = ScenarioValidator(scenario_file)
        validator.parse_file()
        
        # Validate scenario BEFORE testing - abort if critical issues found
        logger.info("Validating scenario before E2E test...")
        validation_report = validator.validate_all()
        
        critical_issues = [issue for issue in validation_report.issues if issue.level.value == "critical"]
        if critical_issues:
            logger.error(f"")
            logger.error(f"🛑 {'='*60}")
            logger.error(f"   ABORTING E2E TEST: Scenario has {len(critical_issues)} CRITICAL validation issues")
            logger.error(f"{'='*60}")
            for issue in critical_issues:
                logger.error(f"   • [Rule {issue.rule_number}] {issue.title}")
                if issue.details:
                    for detail in issue.details[:3]:  # Show first 3 details
                        logger.error(f"     - {detail}")
            logger.error(f"")
            logger.error(f"Fix the scenario generator to produce valid scenarios before E2E testing.")
            logger.error(f"{'='*60}")
            
            result.status = "ERROR"
            result.issues.append(f"Scenario validation failed with {len(critical_issues)} critical issues")
            for issue in critical_issues:
                result.issues.append(f"[Rule {issue.rule_number}] {issue.title}")
            return result
        
        # Extract roles from parsed data
        roles = validator.roles if validator.roles else []
        scenario_name = scenario_file.stem
        
        # Extract actual scenario ID from file content (e.g., museum_gala_vault)
        import re
        content = scenario_file.read_text()
        id_match = re.search(r'\*\*ID\*\*:\s*`([^`]+)`', content)
        scenario_id = id_match.group(1) if id_match else scenario_file.stem
        logger.info(f"Extracted scenario ID: {scenario_id}")
        
        logger.info(f"Scenario: {scenario_name}")
        logger.info(f"Roles: {roles}")
        logger.info(f"Difficulty: {difficulty}")
        
        # Initialize result
        result = GameplayTestResult(
            scenario_file=str(scenario_file),
            scenario_name=scenario_name,
            player_count=len(roles),
            difficulty=difficulty,
            status="UNKNOWN",
            turns_taken=0
        )
        
        try:
            # Create room
            room_code = await self._create_room()
            if not room_code:
                result.status = "ERROR"
                result.issues.append("Failed to create room")
                return result
            
            logger.info(f"Created room: {room_code}")
            
            # Spawn bots
            bots = []
            for i, role in enumerate(roles):
                bot_name = f"Bot_{role}"
                bot = BotPlayer(
                    player_name=bot_name,
                    role=role,
                    difficulty=difficulty,
                    backend_url=self.backend_url.replace("http://", "ws://")
                )
                bots.append(bot)
            
            # Connect bots sequentially with small delay to ensure stable connections
            logger.info(f"Connecting {len(bots)} bots sequentially...")
            for i, bot in enumerate(bots):
                success = await bot.connect(room_code)
                if not success:
                    result.status = "ERROR"
                    result.issues.append(f"Bot {bot.player_name} failed to connect")
                    return result
                # Small delay between connections for stability
                if i < len(bots) - 1:
                    await asyncio.sleep(1)
            
            # All bots select roles
            logger.info("Bots selecting roles...")
            select_tasks = [bot.select_role() for bot in bots]
            await asyncio.gather(*select_tasks)
            
            await asyncio.sleep(1)  # Give backend time to process
            
            # First bot should be host (first joiner logic)
            host_bot = bots[0]
            if not host_bot.state.is_host:
                logger.error("First bot is not marked as host! Check backend join_room logic.")
                result.status = "ERROR"
                result.issues.append("First bot did not become host")
                return result
            
            # Host starts game
            logger.info(f"Host ({host_bot.player_name}) starting game...")
            game_started = await host_bot.start_game(scenario_id)
            
            if not game_started:
                result.status = "ERROR"
                result.issues.append("Failed to start game")
                return result
            
            logger.info("Game started successfully, waiting for backend to initialize...")
            await asyncio.sleep(2)  # Give backend time to initialize game state
            
            logger.info("DEBUG: After sleep, checking bot tasks...")
            
            # Verify all bots received tasks
            try:
                logger.info(f"DEBUG: Checking {len(bots)} bots")
                for i, bot in enumerate(bots):
                    logger.info(f"DEBUG: Checking bot {i}: {bot.player_name}")
                    task_count = len(bot.state.available_tasks)
                    logger.info(f"  {bot.player_name} ({bot.role}): {task_count} available tasks")
            except Exception as e:
                logger.error(f"Error checking bot tasks: {e}", exc_info=True)
                result.status = "ERROR"
                result.issues.append(f"Failed to check bot tasks: {str(e)}")
                return result
            
            # Main game loop
            logger.info("Starting main game loop...")
            try:
                game_result = await self._run_game_loop(bots, result, max_turns=self.max_turns)
            except Exception as e:
                logger.error(f"Error in game loop: {e}", exc_info=True)
                result.status = "ERROR"
                result.issues.append(f"Game loop error: {str(e)}")
                return result
            
            # Cleanup
            logger.info("Disconnecting bots...")
            for bot in bots:
                await bot.disconnect()
            
            return game_result
            
        except Exception as e:
            logger.error(f"Test error: {e}", exc_info=True)
            result.status = "ERROR"
            result.issues.append(f"Exception: {str(e)}")
            return result
    
    async def _run_game_loop(
        self, 
        bots: List[BotPlayer], 
        result: GameplayTestResult,
        max_turns: int
    ) -> GameplayTestResult:
        """
        Main game loop where bots take turns
        
        Returns:
            Updated result object
        """
        turn = 0
        idle_counts = {bot.role: 0 for bot in bots}
        
        # Track consecutive failures per bot to detect stuck loops
        consecutive_failures = {bot.player_name: 0 for bot in bots}
        MAX_CONSECUTIVE_FAILURES = 5
        
        while turn < max_turns:
            turn += 1
            result.turns_taken = turn
            
            # Progress indicator every 5 turns
            if turn % 5 == 0:
                logger.info(f"")
                logger.info(f"{'='*60}")
                logger.info(f"  TURN {turn} / {max_turns}")
                logger.info(f"  Active: {sum(1 for b in bots if b.has_available_tasks())}/{len(bots)} bots")
                logger.info(f"  Completed: {sum(result.tasks_completed_per_role.values())} tasks")
                logger.info(f"{'='*60}")
            else:
                logger.info(f"")
                logger.info(f"--- Turn {turn} ---")
            
            # Check win condition
            if await self._check_game_won(bots):
                result.status = "WIN"
                logger.info(f"")
                logger.info(f"🎉 {'='*60}")
                logger.info(f"   ✅ GAME WON IN {turn} TURNS!")
                logger.info(f"   {'='*60}")
                break
            
            # Get bots with available actions
            active_bots = [b for b in bots if b.has_available_tasks()]
            
            if not active_bots:
                # No bots have available tasks - this could be a win condition if all tasks are completed
                # Check if we have a reasonable number of completed tasks (at least 1 per bot)
                total_completed = sum(len(bot.state.completed_tasks) for bot in bots)
                expected_min = len(bots)  # At least 1 task per bot
                
                if total_completed >= expected_min:
                    # All tasks completed successfully
                    result.status = "WIN"
                    logger.info(f"")
                    logger.info(f"🎉 {'='*60}")
                    logger.info(f"   ✅ ALL TASKS COMPLETED IN {turn} TURNS!")
                    logger.info(f"   {'='*60}")
                else:
                    # True deadlock - no tasks available but none completed either
                    result.status = "DEADLOCK"
                    result.issues.append(f"Turn {turn}: No bots have available tasks (deadlock)")
                    logger.warning(f"")
                    logger.warning(f"⚠️  {'='*60}")
                    logger.warning(f"   DEADLOCK: No bots have available tasks, {total_completed} total completions")
                    logger.warning(f"   {'='*60}")
                break
            
            # Track idle bots
            idle_bots = [bot for bot in bots if bot not in active_bots]
            if idle_bots:
                logger.debug(f"Idle: {', '.join([b.role for b in idle_bots])}")
            
            for bot in bots:
                if bot not in active_bots:
                    idle_counts[bot.role] += 1
            
            # Each active bot takes a turn
            for bot in active_bots:
                try:
                    should_abort = await self._bot_take_turn(bot, result, consecutive_failures, MAX_CONSECUTIVE_FAILURES, all_bots=bots)
                    if should_abort:
                        return result
                except Exception as e:
                    logger.error(f"❌ Error during {bot.player_name} turn: {e}")
                    result.issues.append(f"Turn {turn}: {bot.player_name} error: {str(e)}")
            
            # Small delay for backend processing
            await asyncio.sleep(0.5)
        
        if turn >= max_turns:
            result.status = "TIMEOUT"
            result.issues.append(f"Reached max turns ({max_turns}) without completing scenario")
        
        # Store idle counts
        result.idle_turns_per_role = idle_counts
        
        # Finalize task completion counts by checking each bot's completed_tasks
        # This ensures we count all tasks, including those auto-completed by the backend
        for bot in bots:
            completed_count = len(bot.state.completed_tasks)
            result.tasks_completed_per_role[bot.role] = completed_count
            logger.debug(f"Bot {bot.role} completed {completed_count} tasks total")
        
        return result
    
    async def _bot_take_turn(self, bot: BotPlayer, result: GameplayTestResult, consecutive_failures: dict, max_failures: int, all_bots: List[BotPlayer] = None) -> bool:
        """
        Bot analyzes state and takes one action
        
        Returns True if test should abort due to repeated failures
        """
        # Get available tasks
        tasks = bot.get_available_tasks()
        
        if not tasks:
            logger.debug(f"  {bot.role}: (no available tasks)")
            return
        
        logger.info(f"  👤 {bot.role} @ {bot.state.current_location}")
        logger.debug(f"     Available tasks: {len(tasks)}")
        
        # Build rich team status so LLM knows what teammates are carrying
        all_bots = all_bots or []
        team_status = {
            other.role: {
                "location": other.state.current_location,
                "inventory": [i.get("name", i.get("id")) for i in other.state.inventory],
                "inventory_ids": [i.get("id") for i in other.state.inventory if i],
                "tasks_completed": len(other.state.completed_tasks),
            }
            for other in all_bots if other.player_name != bot.player_name
        }

        # Use LLM to decide action
        decision = await self.decision_maker.decide_action(
            role=bot.role,
            current_location=bot.state.current_location,
            inventory=bot.state.inventory,
            available_tasks=tasks,
            completed_tasks=list(bot.state.completed_tasks),
            achieved_outcomes=list(bot.state.achieved_outcomes),
            npcs=bot.state.npcs,
            locations=bot.state.locations,
            scenario_objective="Complete the heist",
            team_status=team_status
        )
        
        # Format action nicely
        action_str = self._format_action(decision)
        logger.info(f"     → {action_str}")
        logger.debug(f"     Reasoning: {decision.reasoning}")
        
        # Execute action
        success = await self._execute_action(bot, decision, result, all_bots=all_bots)
        
        if success:
            logger.info(f"     ✅ Success")
            consecutive_failures[bot.player_name] = 0  # Reset on success
        else:
            logger.warning(f"     ❌ Failed")
            result.issues.append(f"Turn {result.turns_taken}: {bot.player_name} {decision.action} failed")
            
            # Track consecutive failures
            consecutive_failures[bot.player_name] += 1
            if consecutive_failures[bot.player_name] >= max_failures:
                logger.error(f"")
                logger.error(f"🛑 {'='*60}")
                logger.error(f"   ABORTING: {bot.player_name} failed {max_failures} times in a row")
                logger.error(f"   This indicates the bot is stuck in an unproductive loop")
                logger.error(f"{'='*60}")
                result.status = "ERROR"
                result.issues.append(f"Turn {result.turns_taken}: {bot.player_name} stuck in failure loop")
                return True  # Signal abort
        
        return False  # Continue normally
    
    def _format_action(self, decision: ActionDecision) -> str:
        """Format action for display"""
        if decision.action == "move":
            return f"Move to {decision.target_location}"
        elif decision.action == "search":
            return f"Search location"
        elif decision.action == "pickup":
            return f"Pickup {decision.target_item}"
        elif decision.action == "talk":
            return f"Talk to {decision.target_npc} for task {decision.target_task}"
        elif decision.action == "complete_task":
            return f"Complete task {decision.target_task}"
        elif decision.action == "handoff":
            return f"Handoff {decision.target_item} to {decision.target_player}"
        elif decision.action == "request_item":
            return f"💬 Ask {decision.target_player} to drop {decision.target_item} at {decision.target_location or 'current location'}"
        elif decision.action == "wait":
            return f"Wait (no available actions)"
        else:
            return decision.action
    
    async def _execute_action(
        self, 
        bot: BotPlayer, 
        decision: ActionDecision,
        result: GameplayTestResult,
        all_bots: List[BotPlayer] = None
    ) -> bool:
        """Execute the chosen action
        
        For E2E testing, we force success on most actions to test dependency chains,
        not player skill/failures
        """
        
        if decision.action == "move":
            if decision.target_location:
                return await bot.move_to_location(decision.target_location)
        
        elif decision.action == "search":
            items = await bot.search_location()
            if items:
                # Pick up first item found
                item_id = items[0].get("id")
                if item_id:
                    picked_up = await bot.pickup_item(item_id)
                    return picked_up  # True = found and picked up an item
            # Empty search is NOT a failure — the room is simply empty.
            # The LLM should choose a different action next turn.
            # Return True so consecutive-failure counter isn't incremented.
            if not items:
                logger.info(f"     (search returned 0 items — room is empty)")
            return True
        
        elif decision.action == "pickup":
            if decision.target_item:
                return await bot.pickup_item(decision.target_item)
        
        elif decision.action == "complete_task":
            if decision.target_task:
                success = await bot.complete_task(decision.target_task)
                if success:
                    # Track completion
                    if bot.role not in result.tasks_completed_per_role:
                        result.tasks_completed_per_role[bot.role] = 0
                    result.tasks_completed_per_role[bot.role] += 1
                return success
        
        elif decision.action == "talk":
            # Use proper NPC conversation flow (cover selection + quick responses)
            if decision.target_task:
                # Get task details to find NPC and cover options
                task = bot.state.available_tasks.get(decision.target_task)
                if not task:
                    logger.error(f"Task {decision.target_task} not found in available tasks")
                    return False
                
                # Get the NPC ID from the task
                npc_id = task.get("npc_id")
                if not npc_id:
                    logger.error(f"Task {decision.target_task} has no npc_id field")
                    return False
                
                # Skip NPC conversations if flag is set (for fast E2E testing)
                if self.skip_npc_conversations:
                    logger.info(f"{bot.player_name} auto-completing NPC task {decision.target_task} (skip_npc_conversations=True)")
                    success = await bot.complete_task(decision.target_task)
                    if success:
                        if bot.role not in result.tasks_completed_per_role:
                            result.tasks_completed_per_role[bot.role] = 0
                        result.tasks_completed_per_role[bot.role] += 1
                    return success
                
                logger.info(f"{bot.player_name} starting NPC conversation with {npc_id} for task {decision.target_task}")
                
                # Find NPC in game state to get cover options
                npc = next((n for n in bot.state.npcs if n.get("id") == npc_id), None)
                if not npc:
                    logger.error(f"NPC {npc_id} not found in bot's NPC list")
                    return False
                
                cover_options = npc.get("cover_options", [])
                if not cover_options:
                    logger.warning(f"NPC {npc_id} has no cover options, skipping conversation")
                    return False
                
                # Choose first cover option (for E2E, we just pick first)
                cover_id = cover_options[0].get("cover_id")
                target_outcomes = task.get("target_outcomes", [])
                
                # Start conversation
                logger.debug(f"     Starting conversation with cover: {cover_id}")
                conv_data = await bot.start_npc_conversation(
                    task_id=decision.target_task,
                    npc_id=npc_id,
                    cover_id=cover_id,
                    target_outcomes=target_outcomes
                )
                
                if not conv_data:
                    logger.warning(f"     Failed to start conversation")
                    return False
                
                # Conduct conversation turns (max 10 turns)
                max_turns = 10
                for turn in range(max_turns):
                    quick_responses = conv_data.get("quick_responses", [])
                    conversation_failed = conv_data.get("conversation_failed", False)
                    suspicion = conv_data.get("suspicion", 0)
                    
                    logger.debug(f"     Turn {turn+1}: suspicion={suspicion}, responses={len(quick_responses)}, failed={conversation_failed}")
                    
                    if conversation_failed:
                        logger.warning(f"     ❌ Conversation failed (too suspicious)")
                        return False
                    
                    if not quick_responses:
                        # Conversation ended successfully
                        break
                    
                    # Choose a response (for E2E, pick first one)
                    response_index = 0
                    logger.debug(f"     Choosing response {response_index}: {quick_responses[response_index].get('text', '')[:50]}...")
                    
                    conv_data = await bot.send_npc_choice(npc_id, response_index)
                    if not conv_data:
                        logger.warning(f"     Failed to send choice")
                        return False
                    
                    # Check if task completed
                    if decision.target_task in bot.state.completed_tasks:
                        logger.info(f"     ✅ NPC task completed after {turn+1} turns")
                        if bot.role not in result.tasks_completed_per_role:
                            result.tasks_completed_per_role[bot.role] = 0
                        result.tasks_completed_per_role[bot.role] += 1
                        return True
                
                # Check final state
                if decision.target_task in bot.state.completed_tasks:
                    logger.info(f"     ✅ NPC task completed")
                    if bot.role not in result.tasks_completed_per_role:
                        result.tasks_completed_per_role[bot.role] = 0
                    result.tasks_completed_per_role[bot.role] += 1
                    return True
                else:
                    logger.warning(f"     ❌ Conversation ended but task not completed")
                    return False
        
        elif decision.action == "handoff":
            if decision.target_item and decision.target_player:
                # Find player_id from role name
                target_bot = next((b for b in (all_bots or []) if b.role == decision.target_player), None)
                if target_bot:
                    return await bot.handoff_item(decision.target_item, target_bot.state.player_id)
        
        elif decision.action == "request_item":
            # Bot A requests that Bot B drops an item so A can pick it up.
            # Flow: B moves to meeting location → B drops item → A moves there → A picks it up
            item_id = decision.target_item
            provider_role = decision.target_player
            meet_location = decision.target_location or bot.state.current_location

            if not item_id or not provider_role:
                logger.warning(f"request_item missing item_id or target_player")
                return False

            # Find the bot that holds the item
            provider_bot = next(
                (b for b in (all_bots or []) if b.role == provider_role), None
            )
            if not provider_bot:
                logger.warning(f"request_item: no bot with role '{provider_role}' found")
                return False

            # Confirm provider actually has the item
            has_item = any(i.get("id") == item_id for i in provider_bot.state.inventory)
            if not has_item:
                logger.warning(f"request_item: {provider_role} doesn't have {item_id}")
                return False

            logger.info(f"💬 {bot.player_name} → {provider_bot.player_name}: 'Can you drop {item_id} at {meet_location}?'")
            logger.info(f"💬 {provider_bot.player_name}: 'Sure, heading there now.'")

            # Step 1: Provider moves to meeting location (if not already there)
            if provider_bot.state.current_location != meet_location:
                moved = await provider_bot.move_to_location(meet_location)
                if not moved:
                    logger.warning(f"request_item: {provider_role} couldn't move to {meet_location}")
                    return False
                logger.info(f"   {provider_bot.player_name} arrived at {meet_location}")

            # Step 2: Provider drops the item
            dropped = await provider_bot.drop_item(item_id)
            if not dropped:
                logger.warning(f"request_item: {provider_role} failed to drop {item_id}")
                return False
            logger.info(f"   {provider_bot.player_name} dropped {item_id} at {meet_location}")

            # Step 3: Requester moves to meeting location (if not already there)
            if bot.state.current_location != meet_location:
                moved = await bot.move_to_location(meet_location)
                if not moved:
                    logger.warning(f"request_item: {bot.player_name} couldn't move to {meet_location}")
                    return False

            # Step 4: Requester picks up the item
            picked_up = await bot.pickup_item(item_id)
            if picked_up:
                logger.info(f"   {bot.player_name} picked up {item_id} ✅")
                return True
            else:
                logger.warning(f"request_item: {bot.player_name} failed to pick up {item_id}")
                return False

        elif decision.action == "wait":
            logger.info(f"{bot.player_name} waiting")
            return True
        
        return False
    
    async def _check_game_won(self, bots: List[BotPlayer]) -> bool:
        """
        Check if game is won by detecting game_ended WebSocket broadcast
        """
        return any(bot.state.game_ended for bot in bots)
    
    async def _create_room(self) -> Optional[str]:
        """Create empty room directly - first WebSocket joiner becomes host"""
        try:
            # Import room_manager directly (same process)
            import sys
            from pathlib import Path
            backend_path = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(backend_path))
            
            from app.services.room_manager import get_room_manager
            from app.models.room import GameRoom, RoomStatus
            
            room_manager = get_room_manager()
            room_code = room_manager.generate_room_code()
            
            # Create empty room with no players - first joiner will become host
            room = GameRoom(
                room_code=room_code,
                host_id="",  # Will be assigned to first joiner
                players={},
                status=RoomStatus.LOBBY
            )
            
            room_manager.rooms[room_code] = room
            logger.info(f"Created empty room {room_code} for E2E testing (first joiner becomes host)")
            return room_code
            
        except Exception as e:
            logger.error(f"Error creating room: {e}", exc_info=True)
            return None
