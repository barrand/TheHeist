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
    action: Literal["move", "search", "pickup", "talk", "complete_task", "handoff", "wait"]
    reasoning: str
    
    # Action-specific parameters
    target_location: Optional[str] = None
    target_item: Optional[str] = None
    target_task: Optional[str] = None
    target_npc: Optional[str] = None
    target_player: Optional[str] = None
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
            task_type = task.get("type", "unknown")
            task_location = task.get("location", "unknown")
            task_desc = task.get("description", "")
            prereqs = task.get("prerequisites", [])
            
            prereq_str = ""
            if prereqs:
                prereq_items = [p for p in prereqs if p.get("type") == "item"]
                if prereq_items:
                    prereq_str = f" (needs: {', '.join([p['id'] for p in prereq_items])})"
            
            tasks_str += f"{i}. [{task_type}] {task_desc} @ {task_location}{prereq_str}\n"
        
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
        
        # Format team status
        team_str = ""
        if team_status:
            for player_role, status in team_status.items():
                team_str += f"- {player_role}: {status}\n"
        
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

TEAM STATUS:
{team_str if team_str else "(no info about teammates)"}

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
5. If nothing else, wait for teammates to complete their prerequisites

DECISION RULES:
- If you have an available task at your current location → complete it
- If you have an available task elsewhere → move to that location
- If a task needs an item → search for it or wait for teammate to handoff
- If stuck with no tasks → wait (teammates need to complete something first)
- For NPC tasks, you'll have separate conversation handling

OUTPUT FORMAT (JSON):
{{
  "action": "move" | "search" | "pickup" | "complete_task" | "handoff" | "wait",
  "reasoning": "Why you chose this action (1-2 sentences)",
  "target_location": "location_id" (if action=move),
  "target_item": "item_id" (if action=pickup),
  "target_task": "task_id" (if action=complete_task),
  "target_player": "role" (if action=handoff)
}}

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
