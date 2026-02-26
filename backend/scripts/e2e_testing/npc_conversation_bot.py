"""
NPC Conversation Bot

Conducts conversations with NPCs to achieve target outcomes.
Uses LLM to select best responses from quick-response options.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import google.generativeai as genai
import aiohttp

from ..config import GEMINI_API_KEY, GEMINI_EXPERIENCE_MODEL

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


@dataclass
class ConversationResult:
    """Result of an NPC conversation"""
    success: bool
    outcomes_achieved: List[str]
    turns_taken: int
    suspicion_final: int
    reason: str  # Why it succeeded or failed


class NPCConversationBot:
    """
    Conducts full conversations with NPCs to achieve target outcomes.
    
    Strategy:
    1. Start conversation with appropriate cover story
    2. Analyze NPC responses and quick-response options
    3. Use LLM to select best response option
    4. Monitor suspicion level
    5. Continue until all outcomes achieved or failure
    """
    
    def __init__(
        self, 
        backend_url: str = "http://localhost:8000",
        model_name: str = None
    ):
        self.backend_url = backend_url
        self.model_name = model_name or GEMINI_EXPERIENCE_MODEL
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.8,
                "response_mime_type": "application/json"
            }
        )
        logger.info(f"NPC Conversation Bot initialized with {self.model_name}")
    
    async def converse_with_npc(
        self,
        room_code: str,
        player_id: str,
        task_id: str,
        npc_id: str,
        npc_name: str,
        target_outcomes: List[str],
        cover_stories: List[Dict],
        difficulty: str = "medium",
        max_turns: int = 12
    ) -> ConversationResult:
        """
        Conduct full conversation with NPC
        
        Args:
            room_code: Game room code
            player_id: Bot's player ID
            task_id: Task ID for this conversation
            npc_id: NPC identifier
            npc_name: NPC display name
            target_outcomes: Outcomes we want to achieve
            cover_stories: Available cover stories
            difficulty: Game difficulty (affects starting suspicion)
            max_turns: Maximum conversation turns
        
        Returns:
            ConversationResult with success status and details
        """
        
        # Choose best cover story
        cover_id = self._choose_cover_story(cover_stories, target_outcomes)
        logger.info(f"Starting conversation with {npc_name}, targeting outcomes: {target_outcomes}")
        logger.info(f"Using cover story: {cover_id}")
        
        # Start conversation
        conversation_state = await self._start_conversation(
            room_code, player_id, task_id, npc_id, cover_id
        )
        
        if not conversation_state:
            return ConversationResult(
                success=False,
                outcomes_achieved=[],
                turns_taken=0,
                suspicion_final=5,
                reason="Failed to start conversation"
            )
        
        turns = 1
        conversation_history = []
        achieved_outcomes = set()
        
        # Main conversation loop
        while turns < max_turns:
            # Check if all outcomes achieved
            current_outcomes = set(conversation_state.get("outcomes_achieved", []))
            achieved_outcomes.update(current_outcomes)
            
            if all(outcome in achieved_outcomes for outcome in target_outcomes):
                logger.info(f"All target outcomes achieved in {turns} turns!")
                return ConversationResult(
                    success=True,
                    outcomes_achieved=list(achieved_outcomes),
                    turns_taken=turns,
                    suspicion_final=conversation_state.get("suspicion", 0),
                    reason="All outcomes achieved"
                )
            
            # Check if suspicion too high
            suspicion = conversation_state.get("suspicion", 0)
            if suspicion >= 5:
                logger.warning(f"Conversation failed: suspicion = {suspicion}")
                return ConversationResult(
                    success=False,
                    outcomes_achieved=list(achieved_outcomes),
                    turns_taken=turns,
                    suspicion_final=suspicion,
                    reason="Suspicion reached maximum (5)"
                )
            
            # Get quick response options
            options = conversation_state.get("quick_responses", [])
            if not options:
                logger.warning("No response options available")
                break
            
            # Use LLM to choose best option
            chosen_idx = await self._choose_response(
                npc_name=npc_name,
                target_outcomes=target_outcomes,
                achieved_outcomes=list(achieved_outcomes),
                suspicion=suspicion,
                conversation_history=conversation_history,
                options=options
            )
            
            chosen_text = options[chosen_idx]
            logger.info(f"Turn {turns}: Chose option {chosen_idx + 1}: {chosen_text[:50]}...")
            
            # Send response
            conversation_state = await self._send_response(
                room_code, player_id, task_id, npc_id, chosen_text
            )
            
            if not conversation_state:
                break
            
            # Update history
            conversation_history.append({
                "turn": turns,
                "player_said": chosen_text,
                "npc_reply": conversation_state.get("npc_reply", ""),
                "suspicion": conversation_state.get("suspicion", 0),
                "outcomes": list(conversation_state.get("outcomes_achieved", []))
            })
            
            turns += 1
        
        # Max turns reached
        return ConversationResult(
            success=False,
            outcomes_achieved=list(achieved_outcomes),
            turns_taken=turns,
            suspicion_final=conversation_state.get("suspicion", 0) if conversation_state else 5,
            reason=f"Max turns ({max_turns}) reached without achieving all outcomes"
        )
    
    def _choose_cover_story(self, cover_stories: List[Dict], target_outcomes: List[str]) -> str:
        """
        Choose most appropriate cover story
        
        For now, just choose first one. Could be enhanced with LLM analysis.
        """
        if not cover_stories:
            return "default"
        
        return cover_stories[0].get("id", "default")
    
    async def _choose_response(
        self,
        npc_name: str,
        target_outcomes: List[str],
        achieved_outcomes: List[str],
        suspicion: int,
        conversation_history: List[Dict],
        options: List[str]
    ) -> int:
        """
        Use LLM to choose best response option
        
        Returns:
            Index of chosen option (0-based)
        """
        
        # Format conversation history
        history_str = ""
        for entry in conversation_history[-3:]:  # Last 3 turns
            history_str += f"Turn {entry['turn']}:\n"
            history_str += f"  You: {entry['player_said']}\n"
            history_str += f"  NPC: {entry['npc_reply']}\n"
            history_str += f"  Suspicion: {entry['suspicion']}/5\n"
        
        # Format options
        options_str = ""
        for i, opt in enumerate(options, 1):
            options_str += f"{i}. \"{opt}\"\n"
        
        # Remaining outcomes
        remaining = [o for o in target_outcomes if o not in achieved_outcomes]
        
        prompt = f"""You are talking to {npc_name} to achieve specific outcomes.

TARGET OUTCOMES:
{', '.join(target_outcomes)}

ACHIEVED SO FAR:
{', '.join(achieved_outcomes) if achieved_outcomes else '(none yet)'}

STILL NEED:
{', '.join(remaining) if remaining else '(all achieved!)'}

CURRENT SUSPICION: {suspicion}/5
(If suspicion reaches 5, you fail)

CONVERSATION SO FAR:
{history_str if history_str else '(just starting)'}

QUICK RESPONSE OPTIONS:
{options_str}

YOUR GOAL:
Choose the response most likely to:
1. Build rapport with the NPC
2. Lower or maintain suspicion
3. Lead toward achieving the remaining outcomes
4. Avoid raising suspicion unnecessarily

OUTPUT FORMAT (JSON):
{{
  "choice": 1 | 2 | 3,
  "reasoning": "Why this option is best (1-2 sentences)"
}}

Which response should you choose?"""
        
        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text)
            
            choice = data["choice"] - 1  # Convert 1-indexed to 0-indexed
            reasoning = data["reasoning"]
            
            # Validate choice
            if choice < 0 or choice >= len(options):
                logger.warning(f"Invalid choice {choice}, defaulting to 0")
                choice = 0
            
            logger.info(f"LLM chose option {choice + 1}: {reasoning}")
            return choice
            
        except Exception as e:
            logger.error(f"LLM response selection error: {e}, defaulting to first option")
            return 0
    
    async def _start_conversation(
        self,
        room_code: str,
        player_id: str,
        task_id: str,
        npc_id: str,
        cover_id: str
    ) -> Optional[Dict]:
        """Start conversation with NPC via REST API"""
        url = f"{self.backend_url}/api/npc/start-conversation"
        
        payload = {
            "room_code": room_code,
            "player_id": player_id,
            "task_id": task_id,
            "npc_id": npc_id,
            "cover_id": cover_id
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"Failed to start conversation: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return None
    
    async def _send_response(
        self,
        room_code: str,
        player_id: str,
        task_id: str,
        npc_id: str,
        message: str
    ) -> Optional[Dict]:
        """Send response to NPC via REST API"""
        url = f"{self.backend_url}/api/npc/send-message"
        
        payload = {
            "room_code": room_code,
            "player_id": player_id,
            "task_id": task_id,
            "npc_id": npc_id,
            "message": message
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"Failed to send message: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
