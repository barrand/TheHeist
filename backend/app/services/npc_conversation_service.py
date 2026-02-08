"""
NPC Conversation Service
Handles NPC conversations with cover fit score system, suspicion tracking,
and structured outcome detection.

Uses Gemini for NPC dialogue and quick response generation.
Suspicion is calculated server-side from fit scores (not by the LLM).
"""

import logging
import random
import json
import time
from typing import Optional, List, Dict, Tuple
import requests

from app.models.npc import QuickResponseOption
from app.models.game_state import (
    NPCData, NPCInfoItem, NPCAction, NPCCoverOption, GameState
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Suspicion change table: fit_score -> {difficulty -> delta}
# Good responses (4-5) reduce suspicion so players can recover.
# Bad responses (1-2) are punishing, especially on hard.
SUSPICION_TABLE = {
    5: {"easy": -2, "medium": -1, "hard": -1},
    4: {"easy": -1, "medium": -1, "hard": 0},
    3: {"easy": 0, "medium": 0, "hard": 1},
    2: {"easy": 1, "medium": 2, "hard": 2},
    1: {"easy": 2, "medium": 3, "hard": 3},
}

COOLDOWN_DURATION_SECONDS = 60  # Same for all difficulties

# Max turns before the NPC ends the conversation (escape valve)
MAX_TURNS = {"easy": 10, "medium": 15, "hard": 20}

# Suspicion mood labels for the visible meter
SUSPICION_LABELS = {
    0: "Relaxed",
    1: "Comfortable",
    2: "Curious",
    3: "Cautious",
    4: "Suspicious",
    5: "Done",
}


class ConversationSession:
    """Tracks the state of an active NPC conversation"""
    
    def __init__(self, npc_id: str, player_id: str, cover_id: str, difficulty: str, target_outcomes: List[str] = None):
        self.npc_id = npc_id
        self.player_id = player_id
        self.cover_id = cover_id
        self.difficulty = difficulty
        self.target_outcomes: List[str] = target_outcomes or []
        self.conversation_history: List[Dict] = []
        self.current_responses: List[QuickResponseOption] = []
        self.suspicion: int = 0
    
    def add_message(self, text: str, is_player: bool):
        self.conversation_history.append({
            "role": "player" if is_player else "npc",
            "text": text,
        })


class NPCConversationService:
    """
    Service for NPC conversations with cover fit score system.
    
    Key design:
    - Quick responses have hidden fit scores (1-5)
    - Suspicion is calculated server-side from fit scores
    - The LLM generates dialogue and reports outcomes (info/actions)
    - At least one quick response per turn has fit 4+
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.npc_model = settings.gemini_npc_model
        self.quick_response_model = settings.gemini_quick_response_model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Active conversation sessions: (player_id, npc_id) -> ConversationSession
        self.sessions: Dict[Tuple[str, str], ConversationSession] = {}
        
        logger.info(f"NPC Conversation Service initialized - NPC: {self.npc_model}, QR: {self.quick_response_model}")
    
    def get_session(self, player_id: str, npc_id: str) -> Optional[ConversationSession]:
        return self.sessions.get((player_id, npc_id))
    
    def start_conversation(
        self,
        npc: NPCData,
        cover_id: str,
        player_id: str,
        difficulty: str,
        game_state: GameState,
        target_outcomes: List[str] = None,
    ) -> Tuple[str, List[QuickResponseOption], int]:
        """
        Start a new conversation with an NPC.
        
        Returns: (greeting, quick_responses, suspicion)
        """
        # Check cooldown
        cooldowns = game_state.npc_cooldowns.get(player_id, {})
        if npc.id in cooldowns and time.time() < cooldowns[npc.id]:
            remaining = int(cooldowns[npc.id] - time.time())
            return (
                f"I'm busy right now. Give me some space. (Cooldown: {remaining}s remaining)",
                [],
                0,
            )
        
        # Find the chosen cover
        cover = next((c for c in npc.cover_options if c.cover_id == cover_id), None)
        if not cover:
            logger.error(f"Cover {cover_id} not found for NPC {npc.id}")
            cover = npc.cover_options[0] if npc.cover_options else NPCCoverOption(
                cover_id="unknown", description="Someone at the event",
                trust_level="low", trust_description="An unknown person"
            )
        
        # Create session with target outcomes
        session = ConversationSession(npc.id, player_id, cover_id, difficulty, target_outcomes=target_outcomes or [])
        self.sessions[(player_id, npc.id)] = session
        
        # Store chosen cover in game state
        if player_id not in game_state.chosen_covers:
            game_state.chosen_covers[player_id] = {}
        game_state.chosen_covers[player_id][npc.id] = cover_id
        
        # Reset suspicion for this conversation
        if player_id not in game_state.npc_suspicion:
            game_state.npc_suspicion[player_id] = {}
        game_state.npc_suspicion[player_id][npc.id] = 0
        
        # Generate greeting
        greeting = self._generate_greeting(npc, cover, difficulty)
        session.add_message(greeting, is_player=False)
        
        # Generate first set of quick responses
        quick_responses = self._generate_quick_responses(npc, cover, session, difficulty)
        session.current_responses = quick_responses
        
        logger.info(f"Started conversation: {player_id} -> {npc.id} as '{cover.cover_id}' (difficulty: {difficulty})")
        
        return greeting, quick_responses, 0
    
    def process_player_choice(
        self,
        response_index: int,
        player_id: str,
        npc: NPCData,
        difficulty: str,
        game_state: GameState,
    ) -> Tuple[str, List[str], int, int, List[QuickResponseOption], bool, Optional[float], List[str]]:
        """
        Process a player's quick response choice.
        
        Returns: (npc_response, outcomes, suspicion, suspicion_delta, 
                  next_quick_responses, conversation_failed, cooldown_until, completed_tasks)
        """
        session = self.get_session(player_id, npc.id)
        if not session:
            return ("I don't think we've met.", [], 0, 0, [], False, None, [])
        
        # Get the chosen response and its fit score
        if response_index < 0 or response_index >= len(session.current_responses):
            response_index = 0
        
        chosen = session.current_responses[response_index]
        player_text = chosen.text
        fit_score = chosen.fit_score
        
        # Add player message to history
        session.add_message(player_text, is_player=True)
        
        # Calculate suspicion delta from fit score + difficulty
        delta = SUSPICION_TABLE.get(fit_score, {}).get(difficulty, 0)
        new_suspicion = max(0, min(5, session.suspicion + delta))
        session.suspicion = new_suspicion
        
        # Update game state suspicion
        if player_id not in game_state.npc_suspicion:
            game_state.npc_suspicion[player_id] = {}
        game_state.npc_suspicion[player_id][npc.id] = new_suspicion
        
        logger.info(f"Player chose response (fit={fit_score}): '{player_text}' | suspicion: {session.suspicion - delta} + {delta} = {new_suspicion}")
        
        # Check for failure BEFORE getting NPC response
        if new_suspicion >= 5:
            # Conversation failed - get contextual dismissal
            dismissal = self._generate_failure_dismissal(npc, session, player_text, difficulty)
            session.add_message(dismissal, is_player=False)
            
            # Set cooldown
            cooldown_until = time.time() + COOLDOWN_DURATION_SECONDS
            if player_id not in game_state.npc_cooldowns:
                game_state.npc_cooldowns[player_id] = {}
            game_state.npc_cooldowns[player_id][npc.id] = cooldown_until
            
            # Clean up session
            del self.sessions[(player_id, npc.id)]
            
            logger.info(f"Conversation FAILED: {player_id} -> {npc.id} (suspicion reached 5)")
            
            return (dismissal, [], 5, delta, [], True, cooldown_until, [])
        
        # 2) Turn limit reached -- NPC ends the conversation naturally
        turn_count = len([m for m in session.conversation_history if m['role'] == 'player'])
        max_turns = MAX_TURNS.get(difficulty, 15)
        if turn_count >= max_turns:
            dismissal = "It's been lovely chatting, but I really must get back to my duties. Perhaps we can talk another time."
            session.add_message(dismissal, is_player=False)
            
            cooldown_until = time.time() + COOLDOWN_DURATION_SECONDS
            if player_id not in game_state.npc_cooldowns:
                game_state.npc_cooldowns[player_id] = {}
            game_state.npc_cooldowns[player_id][npc.id] = cooldown_until
            
            del self.sessions[(player_id, npc.id)]
            
            logger.info(f"Conversation timed out after {turn_count} turns (max {max_turns} for {difficulty})")
            return (dismissal, [], new_suspicion, delta, [], True, cooldown_until, [])
        
        # Get NPC response with outcome detection
        cover = next((c for c in npc.cover_options if c.cover_id == session.cover_id), None)
        already_achieved = set(game_state.achieved_outcomes.get(player_id, []))
        npc_response, outcomes = self._get_npc_response(npc, cover, session, player_text, difficulty, already_achieved)
        session.add_message(npc_response, is_player=False)
        
        # Track achieved outcomes
        completed_tasks = []
        if outcomes:
            if player_id not in game_state.achieved_outcomes:
                game_state.achieved_outcomes[player_id] = []
            for outcome_id in outcomes:
                if outcome_id not in game_state.achieved_outcomes[player_id]:
                    game_state.achieved_outcomes[player_id].append(outcome_id)
            
            # NPC task auto-completion is now handled by the API layer
            # via GameStateManager.check_npc_completions() after this returns
        
        # Generate next quick responses
        next_responses = self._generate_quick_responses(npc, cover, session, difficulty)
        session.current_responses = next_responses
        
        return (npc_response, outcomes, new_suspicion, delta, next_responses, False, None, completed_tasks)
    
    def _generate_greeting(self, npc: NPCData, cover: NPCCoverOption, difficulty: str) -> str:
        """Generate NPC's opening line based on cover story and trust level"""
        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}

Someone approaches you at the event. They claim to be: {cover.description}

Your instinct about this cover: {cover.trust_description}

{self._get_difficulty_prompt(difficulty)}

Generate a SHORT greeting (1-2 sentences) that reflects your reaction to this person's cover story.
Be natural and in character. Just the dialogue, no quotes or formatting."""

        try:
            return self._call_llm(prompt, self.npc_model, temperature=0.7, max_tokens=150)
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return f"Oh, hello there. What can I do for you?"
    
    def _generate_quick_responses(
        self, npc: NPCData, cover: Optional[NPCCoverOption], 
        session: ConversationSession, difficulty: str
    ) -> List[QuickResponseOption]:
        """Generate 3 quick responses with random fit scores"""
        
        # Pick random fit targets (at least one must be 4 or 5)
        fit_targets = self._pick_fit_targets()
        
        # Get remaining outcomes the player needs
        remaining_info = [i for i in npc.information_known if i.info_id]
        remaining_actions = npc.actions_available
        outcomes_text = ""
        if remaining_info:
            outcomes_text += "Info player still needs: " + ", ".join(
                [f"{i.info_id}: {i.description}" for i in remaining_info[:3]]
            )
        if remaining_actions:
            outcomes_text += "\nActions player could convince NPC to do: " + ", ".join(
                [f"{a.action_id}: {a.description}" for a in remaining_actions[:2]]
            )
        
        # Build conversation context
        recent = session.conversation_history[-6:]
        context = "\n".join([f"{'Player' if m['role'] == 'player' else npc.name}: {m['text']}" for m in recent])
        
        cover_desc = cover.description if cover else "Someone at the event"
        
        # Build fit level descriptions for the prompt
        fit_descriptions = []
        for fit in fit_targets:
            if fit >= 4:
                fit_descriptions.append(f"Fit {fit}: Perfect/good for the cover. Natural and trust-building.")
            elif fit == 3:
                fit_descriptions.append(f"Fit {fit}: Neutral. Slightly off but not alarming.")
            elif fit == 2:
                fit_descriptions.append(f"Fit {fit}: Poor fit. Awkward for this cover, a perceptive NPC would notice.")
            else:
                fit_descriptions.append(f"Fit {fit}: Terrible fit. Obviously wrong for the cover. Can be funny or absurd.")
        
        prompt = f"""Generate 3 response options for an NPC conversation in a heist game.

Player's cover: {cover_desc}
NPC: {npc.name}, {npc.role}
Conversation so far:
{context if context else "(conversation just started)"}

{outcomes_text}

Generate responses at these cover fit levels: {fit_targets}
{chr(10).join(fit_descriptions)}

Rules:
- Keep each response SHORT: 5-15 words max. Like real dialogue, not paragraphs.
- Higher-fit responses seek info naturally for the cover
- Lower-fit responses feel wrong for THIS cover with THIS NPC
- Fit 1 responses can be funny or absurd
- All should relate to the conversation context

Return ONLY a JSON array (no markdown, no wrapping):
[{{"text": "response text", "fit": {fit_targets[0]}}}, {{"text": "response text", "fit": {fit_targets[1]}}}, {{"text": "response text", "fit": {fit_targets[2]}}}]"""
        
        try:
            raw = self._call_llm(prompt, self.quick_response_model, temperature=0.8, max_tokens=400)
            
            # Parse JSON response
            # Strip markdown code fences if present
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
            
            parsed = json.loads(raw)
            
            responses = []
            for item in parsed[:3]:
                responses.append(QuickResponseOption(
                    text=item["text"],
                    fit_score=int(item["fit"])
                ))
            
            # Shuffle so good options aren't always first
            random.shuffle(responses)
            
            logger.info(f"Generated quick responses: {[(r.text[:40], r.fit_score) for r in responses]}")
            return responses
            
        except Exception as e:
            logger.error(f"Error generating quick responses: {e}", exc_info=True)
            return self._fallback_quick_responses(fit_targets)
    
    def _get_npc_response(
        self, npc: NPCData, cover: Optional[NPCCoverOption],
        session: ConversationSession, player_text: str, difficulty: str,
        already_achieved: set = None,
    ) -> Tuple[str, List[str]]:
        """Get NPC response and detect outcomes via structured JSON"""
        
        cover_desc = cover.description if cover else "Someone at the event"
        trust_desc = cover.trust_description if cover else "An unknown person"
        already_achieved = already_achieved or set()
        target_outcomes = set(session.target_outcomes) if session.target_outcomes else set()
        
        # Separate target outcomes (what player needs) from other NPC knowledge
        target_info_lines = []
        other_info_lines = []
        for item in npc.information_known:
            if item.info_id:
                if item.info_id in already_achieved:
                    continue  # skip already achieved
                elif item.info_id in target_outcomes:
                    target_info_lines.append(f"- [{item.info_id}] {item.description}")
                else:
                    other_info_lines.append(f"- {item.description} (background knowledge, share freely as flavor)")
            else:
                other_info_lines.append(f"- {item.description} (flavor)")
        
        target_action_lines = []
        other_action_lines = []
        for action in npc.actions_available:
            if action.action_id in already_achieved:
                continue
            elif action.action_id in target_outcomes:
                target_action_lines.append(f"- [{action.action_id}] {action.description}")
            else:
                other_action_lines.append(f"- {action.description} (background)")
        
        # Build conversation context
        recent = session.conversation_history[-10:]
        context = "\n".join([f"{'Player' if m['role'] == 'player' else npc.name}: {m['text']}" for m in recent])
        
        # Turn count for pacing
        turn_count = len([m for m in session.conversation_history if m['role'] == 'player'])
        pacing = self._get_pacing_instruction(turn_count, session.suspicion, difficulty, already_achieved, target_outcomes)
        
        # Build the prompt with clear separation of target vs background
        target_section = ""
        if target_info_lines or target_action_lines:
            target_section = "=== PLAYER IS TRYING TO LEARN/ACHIEVE (these are the OUTCOME IDs) ===\n"
            if target_info_lines:
                target_section += "Info to share:\n" + "\n".join(target_info_lines) + "\n"
            if target_action_lines:
                target_section += "Actions to agree to:\n" + "\n".join(target_action_lines) + "\n"
        
        background_section = ""
        if other_info_lines or other_action_lines:
            background_section = "=== Other things you know (share freely as flavor, no IDs needed) ===\n"
            background_section += "\n".join(other_info_lines + other_action_lines) + "\n"
        
        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}
Location: {npc.location}

The person talking to you claims to be: {cover_desc}
Your instinct: {trust_desc}

{target_section}
{background_section}
Current suspicion level: {session.suspicion} out of 5
Conversation turn: {turn_count}

{self._get_difficulty_prompt(difficulty)}

{pacing}

Conversation so far:
{context}

Player just said: "{player_text}"

Rules:
- Stay in character. Be natural and conversational.
- Keep response under 3 sentences.
- When you share target info, include the SPECIFIC details (locations, times, names) in your dialogue.
- When you agree to a target action, say so clearly in your dialogue.

RESPOND AS JSON (no markdown, no wrapping):
{{"response": "your dialogue", "outcomes": ["id1"]}}

Include outcome IDs ONLY for target info/actions you EXPLICITLY shared or agreed to in THIS response.
If nothing was revealed/agreed, use empty array: {{"response": "your dialogue", "outcomes": []}}"""
        
        try:
            raw = self._call_llm(prompt, self.npc_model, temperature=0.7, max_tokens=300)
            
            # Parse JSON
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
            
            parsed = json.loads(raw)
            response_text = parsed.get("response", "...")
            outcomes = parsed.get("outcomes", [])
            
            # Strip quotes from response if present
            response_text = response_text.strip().strip('"')
            
            logger.info(f"NPC response: '{response_text}' | outcomes: {outcomes}")
            return response_text, outcomes
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse NPC JSON response: {e}. Raw: {raw[:200]}")
            # Try to extract just the text
            return raw.strip().strip('"'), []
        except Exception as e:
            logger.error(f"Error getting NPC response: {e}", exc_info=True)
            return "Hmm, let me think about that.", []
    
    def _generate_failure_dismissal(
        self, npc: NPCData, session: ConversationSession,
        last_player_text: str, difficulty: str
    ) -> str:
        """Generate a contextual dismissal when suspicion hits 5"""
        
        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}

You've been talking to someone who has made you very suspicious. Your suspicion is now at maximum.
The last thing they said was: "{last_player_text}"

End this conversation naturally and firmly based on what they just said.
Be in character. 1-2 sentences. Just the dialogue, no quotes or formatting."""
        
        try:
            return self._call_llm(prompt, self.npc_model, temperature=0.7, max_tokens=150)
        except Exception as e:
            logger.error(f"Error generating failure dismissal: {e}")
            return "I don't think I should be talking to you anymore. Please excuse me."
    
    def _get_pacing_instruction(self, turn_count: int, suspicion: int, difficulty: str, already_achieved: set, target_outcomes: set) -> str:
        """Generate pacing instructions based on turn count, difficulty, AND suspicion.
        
        Turn budgets (total turns to get ALL target outcomes):
        - Easy:   4-5 turns  
        - Medium: 5-7 turns  
        - Hard:   6-8 turns  
        
        KEY RULE: High suspicion blocks reveals. The NPC should NOT share
        secrets with someone they're getting suspicious of, regardless of 
        turn count. This creates a real risk of failure.
        """
        remaining = len(target_outcomes - already_achieved)
        
        if remaining == 0:
            return "PACING: All target outcomes achieved. Just chat naturally, no more reveals needed."
        
        # High suspicion blocks reveals regardless of turn count
        if suspicion >= 4:
            return f"""PACING: Turn {turn_count}. Suspicion is {suspicion}/5 -- you are very uncomfortable.
Do NOT share any sensitive information. You're thinking about ending this conversation.
Give short, deflective answers. {remaining} outcome(s) remaining but you're NOT sharing."""
        
        if suspicion >= 3:
            return f"""PACING: Turn {turn_count}. Suspicion is {suspicion}/5 -- something feels off about this person.
Do NOT reveal target outcomes right now. Be evasive and change the subject.
They need to say something that puts you at ease first. {remaining} outcome(s) remaining."""
        
        if difficulty == "easy":
            if turn_count >= 4:
                return f"""PACING (IMPORTANT): Turn {turn_count}. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
You've been chatting for a while and they seem fine. Share one target outcome NOW if their message is at all relevant.
Include specific details (names, locations, times) and the outcome ID."""
            elif turn_count >= 2:
                return f"""PACING: Turn {turn_count}. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
You're warming up to them. If they ask about something you know, you can hint at it but don't give the full details yet."""
            else:
                return f"""PACING: Turn {turn_count}. Early in the conversation. Be friendly and open.
{remaining} outcome(s) to go. Get to know them first before sharing anything sensitive."""
        
        elif difficulty == "hard":
            if turn_count >= 6:
                return f"""PACING (IMPORTANT): Turn {turn_count}. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
They've earned your trust over {turn_count} turns with low suspicion. Share one target outcome NOW if relevant.
Include specific details and the outcome ID."""
            elif turn_count >= 3:
                return f"""PACING: Turn {turn_count}. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
You're getting more comfortable. If they ask a well-crafted question that fits their cover, consider sharing."""
            else:
                return f"""PACING: Turn {turn_count}. Early in the conversation. Be friendly but guarded.
They need to prove they belong before you share anything sensitive. {remaining} outcome(s) to go."""
        
        else:  # medium
            if turn_count >= 5:
                return f"""PACING (IMPORTANT): Turn {turn_count}. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
You've had a good conversation and trust them. Share one target outcome NOW if relevant.
Include specific details and the outcome ID."""
            elif turn_count >= 2:
                return f"""PACING: Turn {turn_count}. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
Getting to know them. If they ask something relevant and their cover makes sense, you can start to open up."""
            else:
                return f"""PACING: Turn {turn_count}. Friendly but not giving away secrets to strangers yet. {remaining} outcome(s) to go."""
    
    def _get_difficulty_prompt(self, difficulty: str) -> str:
        """Get difficulty-specific instructions for the NPC"""
        if difficulty == "easy":
            return """Player difficulty: easy
- Accept their cover story at face value.
- Be friendly and forthcoming. You like talking to people.
- If they ask about something you know, share it willingly.
- Share one tagged item per response when the topic is relevant."""
        elif difficulty == "hard":
            return """Player difficulty: hard
- Be observant and skeptical of their cover. Notice if questions don't fit.
- Require real rapport before sharing sensitive info.
- A well-crafted question that fits the cover naturally still gets an answer.
- NEVER completely stonewall -- always leave an opening for clever players."""
        else:  # medium
            return """Player difficulty: medium
- Be realistic -- friendly but not giving away secrets to strangers.
- After a few turns of good conversation, share info when asked.
- If they ask about something related to your knowledge, give them something useful."""
    
    def _pick_fit_targets(self) -> List[int]:
        """Pick 3 random fit targets, ensuring at least one is 4 or 5"""
        # Ensure at least one high-fit option
        guaranteed_good = random.choice([4, 5])
        
        # The other two are random (weighted toward variety)
        other_options = random.choices(
            [1, 2, 3, 4, 5],
            weights=[15, 20, 25, 25, 15],  # Slight bias toward middle
            k=2
        )
        
        targets = [guaranteed_good] + other_options
        random.shuffle(targets)
        return targets
    
    def _fallback_quick_responses(self, fit_targets: List[int]) -> List[QuickResponseOption]:
        """Fallback responses if LLM fails"""
        fallbacks = [
            QuickResponseOption(text="So what's your role here?", fit_score=max(fit_targets)),
            QuickResponseOption(text="Anything interesting happen tonight?", fit_score=3),
            QuickResponseOption(text="Where do they keep the good stuff?", fit_score=min(fit_targets)),
        ]
        random.shuffle(fallbacks)
        return fallbacks
    
    def _call_llm(self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
        """Call Gemini API and return text response"""
        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    def check_cooldown(self, player_id: str, npc_id: str, game_state: GameState) -> Tuple[bool, int]:
        """Check if player is in cooldown for an NPC. Returns (in_cooldown, seconds_remaining)"""
        cooldowns = game_state.npc_cooldowns.get(player_id, {})
        if npc_id in cooldowns:
            remaining = cooldowns[npc_id] - time.time()
            if remaining > 0:
                return True, int(remaining)
            else:
                # Cooldown expired - clean up
                del cooldowns[npc_id]
                # Also clean up suspicion and cover for fresh start
                if player_id in game_state.npc_suspicion and npc_id in game_state.npc_suspicion[player_id]:
                    del game_state.npc_suspicion[player_id][npc_id]
                if player_id in game_state.chosen_covers and npc_id in game_state.chosen_covers[player_id]:
                    del game_state.chosen_covers[player_id][npc_id]
                # Clean up session
                if (player_id, npc_id) in self.sessions:
                    del self.sessions[(player_id, npc_id)]
        
        return False, 0


# Global service instance
_npc_service: Optional[NPCConversationService] = None


def get_npc_conversation_service() -> NPCConversationService:
    """Get or create global NPC conversation service"""
    global _npc_service
    if _npc_service is None:
        _npc_service = NPCConversationService()
    return _npc_service
