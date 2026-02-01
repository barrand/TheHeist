"""
NPC Conversation Service
Handles real-time NPC chat interactions using Google Gemini API

Uses gemini-1.5-flash-8b for fast, cost-effective conversations during gameplay.
This service is specifically for NPC dialogue - not for image generation or 
experience creation (those are separate services).
"""

import logging
from typing import Optional
import google.generativeai as genai

from app.models.npc import Objective, NPCInfo, ConfidenceLevel
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class NPCConversationService:
    """
    Service for real-time NPC conversations during gameplay
    
    Responsibilities:
    - Generate NPC responses to player messages
    - Detect when objectives are revealed
    - Generate quick response suggestions
    - Manage conversation difficulty levels
    
    NOT responsible for:
    - Image generation (see image_generation_service.py in scripts)
    - Experience generation (see experience_generation_service.py in scripts)
    """
    
    def __init__(self):
        """Initialize Gemini service with API key from settings"""
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"Initialized Gemini service with model: {settings.gemini_model}")
    
    def get_difficulty_instructions(self, difficulty: str) -> str:
        """Get NPC behavior instructions based on difficulty setting"""
        instructions = {
            "easy": """
- Be helpful and forthcoming
- Share information after 1-2 questions
- Give clear hints if they're on the right track
""",
            "hard": """
- Be cautious and suspicious
- Require significant rapport building
- Only share information if they ask the perfect question
- May lie or mislead if they're too direct
""",
            "medium": """
- Be realistic - friendly but not too forthcoming
- Share information after building some rapport
- Give subtle hints if they're getting warm
"""
        }
        return instructions.get(difficulty.lower(), instructions["medium"])
    
    def build_npc_prompt(
        self,
        npc: NPCInfo,
        objectives: list[Objective],
        player_message: str,
        difficulty: str
    ) -> str:
        """Build the system prompt for NPC conversation"""
        
        # Filter objectives NPC knows about
        known_objectives = [
            obj for obj in objectives
            if obj.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]
        ]
        
        objectives_text = "\n".join([
            f"- {obj.description} ("
            f"{'you definitely know this' if obj.confidence == ConfidenceLevel.HIGH else 'you might know this'}"
            f")"
            for obj in known_objectives
        ])
        
        return f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}
Location: {npc.location}

The player is a member of a heist crew trying to gather information from you.

Information you know (and can share if asked properly):
{objectives_text}

Difficulty: {difficulty}
{self.get_difficulty_instructions(difficulty)}

IMPORTANT: 
- Stay in character at all times
- Be natural and conversational
- Share information gradually, not all at once
- If they ask about something you don't know, you genuinely don't know
- Keep responses under 3 sentences
- Don't be too obvious about having "quest information"

Player says: "{player_message}"

Respond naturally as {npc.name}:"""
    
    async def get_npc_response(
        self,
        npc: NPCInfo,
        objectives: list[Objective],
        player_message: str,
        difficulty: str = "medium"
    ) -> str:
        """
        Get NPC response to player message
        
        Args:
            npc: NPC information
            objectives: List of objectives player is trying to learn
            player_message: What the player said
            difficulty: Conversation difficulty (easy/medium/hard)
            
        Returns:
            NPC's response text
            
        Raises:
            Exception: If Gemini API call fails
        """
        logger.info(f"Getting NPC response: {npc.name} <- '{player_message}'")
        
        try:
            prompt = self.build_npc_prompt(npc, objectives, player_message, difficulty)
            response = self.model.generate_content(prompt)
            npc_text = response.text
            
            logger.info(f"NPC response: '{npc_text}'")
            return npc_text
            
        except Exception as e:
            logger.error(f"Error getting NPC response: {e}", exc_info=True)
            raise
    
    async def generate_quick_responses(
        self,
        npc: NPCInfo,
        objectives: list[Objective],
        conversation_history: list[dict]
    ) -> list[str]:
        """
        Generate 3 quick response suggestions for the player
        
        Args:
            npc: NPC information
            objectives: List of objectives
            conversation_history: Recent conversation messages
            
        Returns:
            List of 3 suggested responses
        """
        logger.info(f"Generating quick responses for {npc.name}")
        
        # Get last few messages for context
        recent_messages = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
        conversation_context = "\n".join([
            f"{'Player' if msg.get('isPlayer') else npc.name}: {msg.get('text', '')}"
            for msg in recent_messages
        ])
        
        incomplete_objectives = [obj for obj in objectives if not obj.is_completed]
        objectives_text = "\n".join([f"- {obj.description}" for obj in incomplete_objectives])
        
        prompt = f"""Generate 3 SHORT response options for a player talking to an NPC in a heist game.

NPC: {npc.name} - {npc.role}
Personality: {npc.personality}

Objectives the player is trying to learn:
{objectives_text}

Recent conversation:
{conversation_context}

Generate 3 SHORT responses (max 10 words each):
1. A safe, friendly option
2. A direct question about one objective
3. A creative/indirect approach

Output ONLY the 3 responses, one per line, no numbers or labels."""
        
        try:
            response = self.model.generate_content(prompt)
            responses = response.text.strip().split('\n')
            responses = [r.strip() for r in responses if r.strip()][:3]
            
            # Ensure we have exactly 3 responses
            if len(responses) < 3:
                responses = self._get_fallback_responses()
            
            logger.info(f"Quick responses: {responses}")
            return responses
            
        except Exception as e:
            logger.error(f"Error generating quick responses: {e}", exc_info=True)
            return self._get_fallback_responses()
    
    def _get_fallback_responses(self) -> list[str]:
        """Get default fallback responses if LLM fails"""
        return [
            "Tell me more about your work here.",
            "Have you noticed anything unusual?",
            "How long have you been in this position?",
        ]
    
    def detect_revealed_objectives(
        self,
        npc_text: str,
        objectives: list[Objective]
    ) -> list[str]:
        """
        Detect which objectives were revealed in the NPC's response
        
        Args:
            npc_text: What the NPC said
            objectives: List of objectives to check
            
        Returns:
            List of objective IDs that were revealed
        """
        revealed = []
        lower_text = npc_text.lower()
        
        for objective in objectives:
            if objective.is_completed:
                continue
            
            # Simple keyword detection
            keywords = objective.description.lower().split()
            keyword_matches = sum(1 for k in keywords if len(k) > 3 and k in lower_text)
            
            # If multiple keywords match, likely revealed
            if keyword_matches >= 2:
                revealed.append(objective.id)
                logger.info(f"Objective revealed: {objective.description}")
        
        return revealed
