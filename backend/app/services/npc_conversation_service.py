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
import re
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

# Max turns before the NPC ends the conversation (tighter = more tension)
MAX_TURNS = {"easy": 8, "medium": 10, "hard": 10}

# Opening mechanic thresholds per difficulty:
# "min"           = minimum turns before any opening can happen
# "high_fits"     = how many fit 4-5 choices needed to earn an opening
# "auto_reveal"   = turn at which NPC auto-reveals (safety net; None = no safety net)
OPENING_THRESHOLDS = {
    "easy":   {"min": 2, "high_fits": 1, "auto_reveal": 7},
    "medium": {"min": 3, "high_fits": 2, "auto_reveal": 9},
    "hard":   {"min": 4, "high_fits": 3, "auto_reveal": None},
}

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
        self.suspicion: int = {"easy": 0, "medium": 2, "hard": 3}.get(difficulty, 0)
        
        # Opening mechanic state
        self.high_fit_count: int = 0       # times player chose fit 4-5
        self.opening_given: bool = False    # NPC has hinted at adjacent topic
        self.opening_topic: str = ""        # what the NPC hinted about (for quick response context)
    
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
                npc_reaction="An unknown person"
            )
        
        # Create session with target outcomes
        session = ConversationSession(npc.id, player_id, cover_id, difficulty, target_outcomes=target_outcomes or [])
        self.sessions[(player_id, npc.id)] = session
        
        # Store chosen cover in game state
        if player_id not in game_state.chosen_covers:
            game_state.chosen_covers[player_id] = {}
        game_state.chosen_covers[player_id][npc.id] = cover_id
        
        # Set starting suspicion based on difficulty
        # Easy: relaxed (0), Medium: cautious (2), Hard: between cautious and suspicious (3)
        starting_suspicion = {"easy": 0, "medium": 2, "hard": 3}.get(difficulty, 0)
        if player_id not in game_state.npc_suspicion:
            game_state.npc_suspicion[player_id] = {}
        game_state.npc_suspicion[player_id][npc.id] = starting_suspicion
        
        # Generate greeting
        greeting = self._generate_greeting(npc, cover, difficulty)
        session.add_message(greeting, is_player=False)
        
        # Generate first set of quick responses
        quick_responses = self._generate_quick_responses(npc, cover, session, difficulty)
        session.current_responses = quick_responses
        
        logger.info(f"Started conversation: {player_id} -> {npc.id} as '{cover.cover_id}' (difficulty: {difficulty})")
        
        return greeting, quick_responses, starting_suspicion
    
    def process_player_choice(
        self,
        response_index: int,
        player_id: str,
        npc: NPCData,
        difficulty: str,
        game_state: GameState,
    ) -> Tuple[str, List[str], int, int, List[QuickResponseOption], bool, Optional[float], List[str], bool]:
        """
        Process a player's quick response choice.
        
        Returns: (npc_response, outcomes, suspicion, suspicion_delta, 
                  next_quick_responses, conversation_failed, cooldown_until, completed_tasks, opening_given)
        """
        session = self.get_session(player_id, npc.id)
        if not session:
            return ("I don't think we've met.", [], 0, 0, [], False, None, [], False)
        
        # Get the chosen response and its fit score
        if response_index < 0 or response_index >= len(session.current_responses):
            response_index = 0
        
        chosen = session.current_responses[response_index]
        player_text = chosen.text
        fit_score = chosen.fit_score
        
        # Track high-fit choices for opening mechanic
        if fit_score >= 4:
            session.high_fit_count += 1
        
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
        
        logger.info(f"Player chose response (fit={fit_score}): '{player_text}' | suspicion: {session.suspicion - delta} + {delta} = {new_suspicion} | high_fits: {session.high_fit_count} | opening_given: {session.opening_given}")
        
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
            
            return (dismissal, [], 5, delta, [], True, cooldown_until, [], False)
        
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
            return (dismissal, [], new_suspicion, delta, [], True, cooldown_until, [], False)
        
        # Get NPC response with outcome detection + opening flag
        cover = next((c for c in npc.cover_options if c.cover_id == session.cover_id), None)
        already_achieved = set(game_state.achieved_outcomes.get(player_id, []))
        npc_response, outcomes, npc_gave_opening = self._get_npc_response(npc, cover, session, player_text, difficulty, already_achieved)
        
        # Opening mechanic tracking
        was_opening = session.opening_given
        if npc_gave_opening and not outcomes:
            # NPC gave an opening but didn't reveal yet -- mark it
            session.opening_given = True
            session.opening_topic = npc_response  # store the NPC text for context
            logger.info(f"🔓 NPC gave an OPENING (high_fits={session.high_fit_count})")
        elif was_opening and not outcomes:
            # Opening was active but player didn't follow up -- close it
            session.opening_given = False
            session.opening_topic = ""
            logger.info(f"❌ Player MISSED the opening (didn't follow up)")
        elif outcomes:
            # Outcome revealed -- opening mechanic complete
            session.opening_given = False
            session.opening_topic = ""
            logger.info(f"✅ Outcome revealed after opening! outcomes={outcomes}")
        
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
        
        # Generate next quick responses (with opening context if active)
        next_responses = self._generate_quick_responses(npc, cover, session, difficulty)
        session.current_responses = next_responses
        
        return (npc_response, outcomes, new_suspicion, delta, next_responses, False, None, completed_tasks, session.opening_given)
    
    def _generate_greeting(self, npc: NPCData, cover: NPCCoverOption, difficulty: str) -> str:
        """Generate NPC's opening line based on cover story and trust level"""
        story_facts = f"\n=== WORLD FACTS (never contradict these) ===\n{npc.story_context}\n" if npc.story_context else ""
        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}
{story_facts}
Someone approaches you at the event. They claim to be: {cover.description}

Your instinct about this person: {cover.npc_reaction}

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
            if fit == 5:
                fit_descriptions.append(f"Fit {fit}: PERFECT for the cover. Something this person would naturally say — builds rapport, reacts to the NPC, or shows knowledge fitting the identity. May occasionally steer toward the objective indirectly, but doesn't have to. Most of the time it's just good, natural conversation.")
            elif fit == 4:
                fit_descriptions.append(f"Fit {fit}: Good for the cover. Plausible and natural, shows familiarity with the role. Might touch on a topic adjacent to the objective, or just be solid rapport-building.")
            elif fit == 3:
                fit_descriptions.append(f"Fit {fit}: Neutral. Generic small talk or a slightly too-direct question about the objective. Doesn't leverage the cover identity. Not suspicious, but doesn't build trust either.")
            elif fit == 2:
                fit_descriptions.append(f"Fit {fit}: Poor. Doesn't fit the cover AND/OR asks about the objective very directly. The NPC would wonder why this person is bringing this up.")
            else:
                fit_descriptions.append(f"Fit {fit}: Terrible. Breaks character, bluntly demands info, or is absurdly off-topic. Should be funny or ridiculous — the kind of thing that makes the player laugh before they pick it.")
        
        # If an opening is active, add context so the generator can create a follow-up option
        opening_context = ""
        if session.opening_given and session.opening_topic:
            # Get just the last NPC message (the opening)
            last_npc_msg = session.opening_topic[:200]
            opening_context = f"""
IMPORTANT - OPENING ACTIVE: The NPC just hinted at something related to their secret knowledge.
Their last message: "{last_npc_msg}"
The HIGHEST-FIT response should naturally follow up on what the NPC just hinted at — ask about the topic they mentioned, show curiosity about their hint.
The other responses should be on different topics or miss the hint entirely.
The player needs to recognize which response follows up on the NPC's hint."""
        
        prompt = f"""Generate 3 response options for an NPC conversation in a heist game.

Player's cover: {cover_desc}
NPC: {npc.name}, {npc.role}
Conversation so far:
{context if context else "(conversation just started)"}

{outcomes_text}
{opening_context}

Generate responses at these cover fit levels: {fit_targets}
{chr(10).join(fit_descriptions)}

KEY PRINCIPLE: Fit score = how natural and in-character the response sounds.
- A fit-5 sounds exactly like something this cover person would say. It builds rapport, reacts naturally, or shows expertise. It does NOT need to mention the objective every time.
- A fit-3 is generic or slightly too direct about the objective. Doesn't use the cover.
- A fit-1 breaks character or bluntly demands info.
- NOT every response should steer toward the objective. Most should just be natural conversation that fits the cover. The objective comes up organically over the course of the conversation.

Rules:
- Keep each response SHORT: 5-15 words max. Like real dialogue, not paragraphs.
- Higher-fit responses should directly reference the cover identity, its interests, or its expertise.
- Lower-fit responses should feel disconnected from the cover — reasonable things a DIFFERENT person might say, but not this cover.
- Fit 1 responses can be funny, absurd, or outright suspicious for someone claiming this identity.
- All should fit the conversational context (respond to what the NPC just said).

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
    ) -> Tuple[str, List[str], bool]:
        """Get NPC response and detect outcomes via structured JSON.
        
        Returns: (response_text, outcome_ids, opening_given)
        """
        
        cover_desc = cover.description if cover else "Someone at the event"
        trust_desc = cover.npc_reaction if cover else "An unknown person"
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
        pacing = self._get_pacing_instruction(turn_count, session.suspicion, difficulty, already_achieved, target_outcomes, session=session)
        
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
        
        relationships = f"\nPeople you know: {npc.relationships}" if npc.relationships else ""
        story_facts = f"\n=== WORLD FACTS (never contradict these) ===\n{npc.story_context}\n" if npc.story_context else ""
        
        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}
Location: {npc.location}{relationships}
{story_facts}

The person talking to you claims to be: {cover_desc}
Your instinct about this person: {trust_desc}

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
- If the player says something odd, off-topic, overly direct, or suspicious, do NOT share any target info. Deflect, change the subject, or express mild confusion. Return empty outcomes.
- Only share target info when the player's message naturally fits the conversation and their cover story. A strange or pushy question should make you MORE guarded, not less.
- When you DO share target info, include the SPECIFIC details (locations, times, names) in your dialogue.
- When you agree to a target action, say so clearly in your dialogue.
- IMPORTANT: If the player says something inconsistent with their claimed cover story, call it out naturally. Reference their cover and note the inconsistency. For example, if they claim to be an art collector but ask about security schedules, you might say "That's an odd question for a collector... I thought you were here about the art?" React with suspicion proportional to how jarring the inconsistency is.

RESPOND AS JSON (no markdown, no wrapping):
{{"response": "your dialogue", "outcomes": ["id1"], "opening": false}}

- "outcomes": Include outcome IDs ONLY for target info/actions you EXPLICITLY shared or agreed to in THIS response. Empty array if nothing revealed.
- "opening": Set to true ONLY when the PACING instruction tells you to give an opening (hint at adjacent topic). Otherwise false.

If nothing was revealed and no opening given: {{"response": "your dialogue", "outcomes": [], "opening": false}}
IMPORTANT: Do NOT include outcome IDs like [vault_location] in the dialogue text. Outcome IDs go ONLY in the "outcomes" array."""
        
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
            opening_flag = parsed.get("opening", False)
            
            # Strip quotes from response if present
            response_text = response_text.strip().strip('"')
            
            # Strip outcome ID tags the LLM may have leaked into dialogue
            # e.g. "[vault_location]" or "[leave_post]"
            response_text = re.sub(r'\s*\[[\w]+\]\s*', ' ', response_text).strip()
            
            logger.info(f"NPC response: '{response_text}' | outcomes: {outcomes} | opening: {opening_flag}")
            return response_text, outcomes, bool(opening_flag)
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse NPC JSON response: {e}. Raw: {raw[:200]}")
            # Try to extract just the text
            return raw.strip().strip('"'), [], False
        except Exception as e:
            logger.error(f"Error getting NPC response: {e}", exc_info=True)
            return "Hmm, let me think about that.", [], False
    
    def _generate_failure_dismissal(
        self, npc: NPCData, session: ConversationSession,
        last_player_text: str, difficulty: str
    ) -> str:
        """Generate a contextual dismissal when suspicion hits 5"""
        
        story_facts = f"\n=== WORLD FACTS (never contradict these) ===\n{npc.story_context}\n" if npc.story_context else ""
        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}
{story_facts}
You've been talking to someone who has made you very suspicious. Your suspicion is now at maximum.
The last thing they said was: "{last_player_text}"

End this conversation naturally and firmly based on what they just said.
Be in character. 1-2 sentences. Just the dialogue, no quotes or formatting."""
        
        try:
            return self._call_llm(prompt, self.npc_model, temperature=0.7, max_tokens=150)
        except Exception as e:
            logger.error(f"Error generating failure dismissal: {e}")
            return "I don't think I should be talking to you anymore. Please excuse me."
    
    def _get_pacing_instruction(self, turn_count: int, suspicion: int, difficulty: str, 
                                already_achieved: set, target_outcomes: set,
                                session: 'ConversationSession' = None) -> str:
        """Generate pacing instructions using the opening mechanic.
        
        Flow:
        1. Before min turns: no hints, no reveals
        2. After min turns + enough high-fit choices: NPC gives an "opening" (hint)
        3. After opening: if player follows up, NPC reveals
        4. Auto-reveal fallback (easy/medium only) as safety net
        
        KEY RULE: High suspicion blocks everything.
        """
        remaining = len(target_outcomes - already_achieved)
        
        if remaining == 0:
            return "PACING: All target outcomes achieved. Just chat naturally, no more reveals needed."
        
        # High suspicion blocks everything regardless of turn count
        if suspicion >= 4:
            return f"""PACING: Turn {turn_count}. Suspicion is {suspicion}/5 -- you are very uncomfortable.
Do NOT share any sensitive information. Do NOT give openings or hints.
Give short, deflective answers. {remaining} outcome(s) remaining but you're NOT sharing."""
        
        if suspicion >= 3:
            return f"""PACING: Turn {turn_count}. Suspicion is {suspicion}/5 -- something feels off about this person.
Do NOT reveal target outcomes or give any hints. Be evasive and change the subject.
They need to say something that puts you at ease first. {remaining} outcome(s) remaining."""
        
        t = OPENING_THRESHOLDS.get(difficulty, OPENING_THRESHOLDS["medium"])
        high_fits = session.high_fit_count if session else 0
        opening_active = session.opening_given if session else False
        
        # Before minimum turns: absolutely no reveals or hints
        if turn_count < t["min"]:
            return f"""PACING (STRICT): Turn {turn_count}. It is TOO EARLY to share anything sensitive or hint at secrets.
Do NOT reveal target outcomes. Do NOT hint at them. You just met this person.
Be friendly, chat, get to know them, but keep secrets to yourself.
{remaining} outcome(s) remaining. Set "opening" to false."""
        
        # Auto-reveal fallback (easy/medium safety net)
        if t["auto_reveal"] and turn_count >= t["auto_reveal"]:
            return f"""PACING (MANDATORY): Turn {turn_count}. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
You have been talking for {turn_count} turns and suspicion is low. You trust this person.
You MUST share one target outcome in this response. This is NOT optional.
Include the outcome ID in the "outcomes" array AND the specific details in your dialogue.
Do not deflect. Do not hint. State the information clearly. Set "opening" to false."""
        
        # OPENING ACTIVE: player needs to follow up
        if opening_active:
            return f"""PACING (FOLLOW-UP): Turn {turn_count}. You just hinted at something related to your secret knowledge.
If the player is following up on your hint -- asking about the topic you mentioned -- then REVEAL the target outcome.
Share the full details and include the outcome ID in the "outcomes" array. Set "opening" to false.
If the player changed the subject or asked about something unrelated, just chat normally.
Do NOT reveal the outcome if they didn't follow up on your hint. Set "opening" to false.
{remaining} outcome(s) remaining. Suspicion {suspicion}/5."""
        
        # Enough rapport to give an opening?
        if high_fits >= t["high_fits"]:
            return f"""PACING (GIVE OPENING): Turn {turn_count}. This person has earned your trust. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
Mention something ADJACENT to your secret knowledge -- a related topic, a vague reference, or a natural segue.
For example, if you know a vault location, you might mention recent security changes, or the east wing, or how paranoid the director has been.
CRITICAL: Do NOT reveal the actual target information yet. Do NOT share specific details like exact locations, codes, or times.
Just create a natural opening the person could follow up on. Tease the topic without answering it.
You MUST set "opening" to true in your response. Keep it natural -- don't force it.
Even if the player asked a direct question, do NOT answer it fully yet -- deflect slightly while mentioning the adjacent topic."""
        
        # Not enough rapport yet
        turns_of_rapport = t["high_fits"] - high_fits
        return f"""PACING: Turn {turn_count}. {remaining} outcome(s) remaining. Suspicion {suspicion}/5.
You're warming up to them but not ready to share anything sensitive.
Chat naturally. You're enjoying the conversation but this person hasn't fully earned your trust yet.
Set "opening" to false."""
    
    def _get_difficulty_prompt(self, difficulty: str) -> str:
        """Get difficulty-specific instructions for the NPC"""
        if difficulty == "easy":
            return """Player difficulty: easy
- Accept their cover story at face value.
- Be friendly and forthcoming. You like talking to people.
- ALWAYS follow the PACING instructions exactly -- they control when you hint and reveal.
- When PACING says to give an opening, make your hint obvious and easy to follow up on."""
        elif difficulty == "hard":
            return """Player difficulty: hard
- Be observant and skeptical of their cover. Notice if questions don't fit.
- Require real rapport before sharing sensitive info.
- ALWAYS follow the PACING instructions exactly -- they control when you hint and reveal.
- When PACING says to give an opening, make it subtle -- a passing mention, not an obvious hint."""
        else:  # medium
            return """Player difficulty: medium
- Be realistic -- friendly but not giving away secrets to strangers.
- ALWAYS follow the PACING instructions exactly -- they control when you hint and reveal.
- When PACING says to give an opening, make it natural but noticeable."""
    
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
