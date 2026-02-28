"""
LLM Decision Maker for Bot Players

Uses Gemini to analyze game state and make intelligent decisions about
what action the bot should take next.
"""

import json
import logging
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
import google.generativeai as genai

from ..config import GEMINI_API_KEY, GEMINI_EXPERIENCE_MODEL

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


@dataclass
class ActionDecision:
    """A decision about what action to take"""
    action: Literal["move", "search", "pickup", "talk", "complete_task", "handoff", "request_item", "wait"]
    reasoning: str
    
    # Action-specific parameters
    target_location: Optional[str] = None
    target_item: Optional[str] = None
    target_task: Optional[str] = None
    target_npc: Optional[str] = None
    target_player: Optional[str] = None  # role name, e.g. "hacker"
    message: Optional[str] = None  # For NPC conversations


class LLMDecisionMaker:
    """
    Uses Gemini to make intelligent decisions about bot actions.
    
    Analyzes:
    - Available tasks and their prerequisites
    - Current location and inventory
    - Team progress (other players' states)
    - Scenario objective
    
    Chooses:
    - What task to work on next
    - What location to move to
    - What items to search for
    - Whether to wait for teammates
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or GEMINI_EXPERIENCE_MODEL
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.7,
                "response_mime_type": "application/json"
            }
        )
        logger.info(f"LLM Decision Maker initialized with {self.model_name}")
    
    async def decide_action(
        self,
        role: str,
        current_location: str,
        inventory: List[Dict],
        available_tasks: List[Dict],
        completed_tasks: List[str],
        achieved_outcomes: List[str],
        npcs: List[Dict],
        locations: List[Dict],
        scenario_objective: str = "",
        team_status: Optional[Dict] = None
    ) -> ActionDecision:
        """
        Decide what action to take next
        
        Args:
            role: Bot's role (mastermind, hacker, etc.)
            current_location: Where bot currently is
            inventory: Items bot has
            available_tasks: Tasks bot can work on
            completed_tasks: Tasks already done
            achieved_outcomes: NPC outcomes already achieved
            npcs: All NPCs in scenario
            locations: All locations in scenario
            scenario_objective: Overall heist goal
            team_status: Info about other players (optional)
        
        Returns:
            ActionDecision with chosen action and reasoning
        """
        
        # Build prompt
        prompt = self._build_prompt(
            role=role,
            current_location=current_location,
            inventory=inventory,
            available_tasks=available_tasks,
            completed_tasks=completed_tasks,
            achieved_outcomes=achieved_outcomes,
            npcs=npcs,
            locations=locations,
            scenario_objective=scenario_objective,
            team_status=team_status
        )
        
        try:
            # Get decision from LLM
            response = self.model.generate_content(prompt)
            decision_data = json.loads(response.text)
            
            # Parse into ActionDecision
            decision = ActionDecision(
                action=decision_data["action"],
                reasoning=decision_data["reasoning"],
                target_location=decision_data.get("target_location"),
                target_item=decision_data.get("target_item"),
                target_task=decision_data.get("target_task"),
                target_npc=decision_data.get("target_npc"),
                target_player=decision_data.get("target_player"),
                message=decision_data.get("message")
            )
            
            logger.info(f"Decision: {decision.action} - {decision.reasoning[:50]}...")
            return decision
            
        except Exception as e:
            logger.error(f"LLM decision error: {e}")
            # Fallback: choose first available task or wait
            return self._fallback_decision(available_tasks, current_location)
    
    def _build_prompt(
        self,
        role: str,
        current_location: str,
        inventory: List[Dict],
        available_tasks: List[Dict],
        completed_tasks: List[str],
        achieved_outcomes: List[str],
        npcs: List[Dict],
        locations: List[Dict],
        scenario_objective: str,
        team_status: Optional[Dict]
    ) -> str:
        """Build the LLM prompt"""
        
        # Format inventory
        inv_str = ", ".join([item.get("name", item.get("id")) for item in inventory])
        if not inv_str:
            inv_str = "(empty)"
        
        # Format available tasks
        tasks_str = ""
        for i, task in enumerate(available_tasks, 1):
            task_id = task.get("id", "unknown")
            task_type = task.get("type", "unknown")
            task_location = task.get("location", "unknown")
            task_desc = task.get("description", "")
            npc_id = task.get("npc_id", "")
            prereqs = task.get("prerequisites", [])
            
            prereq_str = ""
            if prereqs:
                prereq_items = [p for p in prereqs if p.get("type") == "item"]
                if prereq_items:
                    prereq_str = f" (needs: {', '.join([p['id'] for p in prereq_items])})"
            
            npc_str = f" NPC:{npc_id}" if npc_id else ""
            tasks_str += f"{i}. ID:`{task_id}` [{task_type}] {task_desc} @ {task_location}{prereq_str}{npc_str}\n"
        
        if not tasks_str:
            tasks_str = "(no tasks available - possibly waiting for teammates)"
        
        # Format locations
        locations_str = ", ".join([loc.get("name", loc.get("id")) for loc in locations])
        
        # Format NPCs
        npcs_str = ""
        for npc in npcs:
            npc_name = npc.get("name", npc.get("id"))
            npc_role = npc.get("role", "")
            npcs_str += f"- {npc_name} ({npc_role})\n"
        
        # Format team status — rich info about each teammate
        team_str = ""
        if team_status:
            for player_role, status in team_status.items():
                if isinstance(status, dict):
                    loc = status.get("location", "unknown")
                    inv = status.get("inventory", [])
                    inv_names = ", ".join(inv) if inv else "nothing"
                    done = status.get("tasks_completed", 0)
                    team_str += f"- {player_role}: at {loc}, carrying [{inv_names}], {done} tasks done\n"
                else:
                    team_str += f"- {player_role}: {status}\n"

        # Highlight items teammates have that YOU might need
        needed_items_str = ""
        if team_status:
            my_task_items = set()
            for task in available_tasks:
                for prereq in task.get("prerequisites", []):
                    if prereq.get("type") == "item":
                        my_task_items.add(prereq["id"])
                for si in task.get("search_items", []):
                    my_task_items.add(si)
            for player_role, status in team_status.items():
                if isinstance(status, dict):
                    their_items = set(status.get("inventory_ids", []))
                    overlap = my_task_items & their_items
                    if overlap:
                        needed_items_str += f"- {player_role} has items you need: {', '.join(overlap)}\n"

        prompt = f"""You are playing as the {role.upper()} in a heist scenario.

SCENARIO OBJECTIVE:
{scenario_objective}

YOUR ROLE:
You are the {role}. Your job is to complete tasks assigned to you that help the team achieve the objective.

CURRENT STATE:
- Location: {current_location}
- Inventory: {inv_str}
- Completed Tasks: {len(completed_tasks)}
- Achieved Outcomes: {len(achieved_outcomes)}

AVAILABLE TASKS:
{tasks_str}

ALL LOCATIONS:
{locations_str}

NPCs IN SCENARIO:
{npcs_str}

TEAMMATES:
{team_str if team_str else "(no info about teammates)"}

ITEMS YOU NEED THAT TEAMMATES ARE HOLDING:
{needed_items_str if needed_items_str else "(none — all needed items are in the world or already yours)"}

TASK TYPES:
- minigame: Complete task directly (you will auto-succeed)
- npc_llm: Talk to an NPC to achieve outcomes
- search: Search a location for items
- handoff: Give item to another player
- info_share: Share information with teammate (real-life conversation, auto-completes)

YOUR GOAL:
Choose the best next action to help complete the heist. Prioritize:
1. Tasks on the critical path (that unlock other tasks)
2. Tasks you can complete NOW (you have all prerequisites)
3. Gathering items needed for upcoming tasks
4. Moving to locations where you need to be
5. If a teammate has an item you need → request it from them
6. If nothing else, wait for teammates to complete their prerequisites

DECISION RULES:
- If task type is "npc_llm" → use "talk" action (set target_npc and target_task)
- If task type is "minigame" or "info_share" → use "complete_task" action  
- If you have an available task at your current location → complete it or talk to NPC
- If you have an available task elsewhere → move to that location
- If task type is "handoff" → you must be in the SAME LOCATION as the target player to hand off an item.
  - Check TEAMMATES section: if target player is already at your location → use "handoff" action
  - If target player is at a DIFFERENT location → use "move" action to go to their location first
  - Never attempt "handoff" if the target player is not at your current location
- If a task needs an item that a TEAMMATE IS HOLDING → use "request_item" to ask them to drop it
- If a task needs an item that is in the world (not held by anyone) → search the correct location
- If stuck with no tasks → wait (teammates need to complete something first)

OUTPUT FORMAT (JSON):
{{
  "action": "move" | "search" | "pickup" | "talk" | "complete_task" | "handoff" | "request_item" | "wait",
  "reasoning": "Why you chose this action (1-2 sentences)",
  "target_location": "location_id" (if action=move or request_item — where to meet),
  "target_item": "item_id" (if action=pickup or request_item),
  "target_npc": "npc_id from task NPC field" (if action=talk),
  "target_task": "task ID from ID:`` field" (if action=talk or complete_task - use the ID, not description!),
  "target_player": "role name e.g. hacker" (if action=handoff or request_item),
  "message": "opening message" (if action=talk)
}}

⚠️ IMPORTANT: 
- For target_task, use the task ID (e.g., "MM1"), NOT the description!
- For npc_llm tasks, use "talk" action with NPC ID from task's NPC field!
- For request_item: set target_player=the role holding the item, target_item=item_id, target_location=where you want them to drop it (use your current location)

What should you do next?"""
        
        return prompt
    
    def _fallback_decision(self, available_tasks: List[Dict], current_location: str) -> ActionDecision:
        """Simple fallback if LLM fails"""
        if available_tasks:
            # Try first available task
            task = available_tasks[0]
            task_location = task.get("location", "")
            task_id = task.get("id", "")
            
            if task_location == current_location:
                return ActionDecision(
                    action="complete_task",
                    reasoning="Fallback: completing first available task",
                    target_task=task_id
                )
            else:
                return ActionDecision(
                    action="move",
                    reasoning="Fallback: moving to task location",
                    target_location=task_location
                )
        else:
            return ActionDecision(
                action="wait",
                reasoning="Fallback: no available tasks, waiting for teammates"
            )
