"""
NPC Conversation Service
Handles real-time NPC chat interactions using Google Gemini API

Uses gemini-2.5-flash for fast, cost-effective conversations during gameplay.
This service is specifically for NPC dialogue - not for image generation or 
experience creation (those are separate services).

Uses direct REST API instead of google-generativeai library to avoid gRPC issues.
"""

import logging
from typing import Optional
import requests
import json

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
        self.api_key = settings.gemini_api_key
        self.npc_model = settings.gemini_npc_model
        self.quick_response_model = settings.gemini_quick_response_model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        logger.info(f"Initialized NPC Conversation Service - NPC model: {self.npc_model}, Quick response model: {self.quick_response_model}")
    
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
- DO NOT wrap your response in quotation marks
- Write ONLY the dialogue text, no formatting or quotes

Player says: "{player_message}"

Your response as {npc.name} (plain text, no quotes):"""
    
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
            
            # Use direct REST API call
            url = f"{self.base_url}/{self.npc_model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500,  # Increased for complete responses
                }
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Log full API response for debugging
            logger.info(f"NPC API response: {json.dumps(data, indent=2)}")
            
            npc_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Strip leading/trailing quotes if Gemini added them
            npc_text = npc_text.strip()
            if npc_text.startswith('"') and len(npc_text) > 1:
                # Find the matching closing quote
                npc_text = npc_text[1:]  # Remove leading quote
                if npc_text.endswith('"'):
                    npc_text = npc_text[:-1]  # Remove trailing quote
            
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
        logger.info(f"Conversation history length: {len(conversation_history)}")
        
        # Get last few messages for context
        recent_messages = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
        conversation_context = "\n".join([
            f"{'Player' if msg.get('isPlayer') else npc.name}: {msg.get('text', '')}"
            for msg in recent_messages
        ])
        
        logger.info(f"Conversation context: {conversation_context}")
        
        incomplete_objectives = [obj for obj in objectives if not obj.is_completed]
        objectives_text = "\n".join([f"- {obj.description}" for obj in incomplete_objectives])
        
        prompt = f"""Generate 3 player responses for this conversation.

Recent conversation:
{conversation_context}

Objectives: {objectives_text[:100] if objectives_text else "Learn about their work"}

Output 3 responses (one per line, no numbers):
1. Friendly comment
2. Question about objectives
3. Indirect probe"""
        
        try:
            # Use gemini-2.0-flash-lite for quick responses (lightweight, no thinking tokens)
            quick_response_model = "models/gemini-2.0-flash-lite"
            url = f"{self.base_url}/{quick_response_model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 200,  # Lower is fine for 1.5-flash-8b (no thinking tokens)
                }
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"API response data keys: {data.keys()}")
            logger.info(f"API response data: {data}")
            
            response_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            logger.info(f"Raw quick response from API: {response_text}")
            
            # Parse the responses
            responses = response_text.strip().split('\n')
            responses = [r.strip() for r in responses if r.strip()][:3]
            
            # Remove any numbering (1., 2., 3., etc.)
            responses = [r.lstrip('0123456789.-)] ').strip() for r in responses]
            
            logger.info(f"Parsed quick responses (count={len(responses)}): {responses}")
            
            # Ensure we have exactly 3 responses
            if len(responses) < 3:
                logger.warning(f"Only got {len(responses)} responses, using fallback")
                responses = self._get_fallback_responses()
            
            logger.info(f"Final quick responses: {responses}")
            return responses
            
        except Exception as e:
            logger.error(f"Error generating quick responses: {e}", exc_info=True)
            logger.error(f"Returning fallback responses due to error")
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
