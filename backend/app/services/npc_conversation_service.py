"""
NPC Conversation Service — Rapport Mechanic

Core concept: Rapport is a resource the player builds (via good cover conversation)
and spends (via probing for objective information). The NPC reveals secrets only
when rapport is high enough AND the player asks the right question.

Quick responses are generated along a spectrum:
  - Rapport builder  (+rapport, no objective progress)
  - Subtle steer     (neutral rapport, mild objective progress)
  - Direct probe     (-rapport, strong objective progress)
"""

import logging
import random
import json
import re
from typing import Optional, List, Dict, Tuple
import requests

from app.models.npc import QuickResponseOption
from app.models.game_state import (
    NPCData, NPCInfoItem, NPCAction, NPCCoverOption, GameState
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Difficulty tables
# ---------------------------------------------------------------------------

DIFFICULTY_CONFIG = {
    "easy": {
        "starting_rapport": 3.0,
        "reveal_threshold": 3.0,
        "max_turns": 10,
        "rapport_build_range": (1.0, 1.5),   # rapport gain from a rapport-builder
        "probe_cost_range": (0.5, 1.0),       # rapport lost from a direct probe
        "fail_threshold": 0.5,                # rapport below this = NPC ends convo
    },
    "medium": {
        "starting_rapport": 2.0,
        "reveal_threshold": 3.0,
        "max_turns": 12,
        "rapport_build_range": (0.5, 1.0),
        "probe_cost_range": (1.0, 1.5),
        "fail_threshold": 0.5,
    },
    "hard": {
        "starting_rapport": 1.0,
        "reveal_threshold": 4.0,
        "max_turns": 12,
        "rapport_build_range": (0.5, 0.75),
        "probe_cost_range": (1.5, 2.0),
        "fail_threshold": 0.5,
    },
}

RAPPORT_LABELS = {
    5.0: "Trusting",
    4.0: "Comfortable",
    3.0: "Warming Up",
    2.0: "Guarded",
    1.0: "Tense",
    0.0: "Done",
}

def rapport_label(rapport: float) -> str:
    for threshold in sorted(RAPPORT_LABELS.keys(), reverse=True):
        if rapport >= threshold:
            return RAPPORT_LABELS[threshold]
    return "Done"


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

class ConversationSession:
    def __init__(self, npc_id: str, player_id: str, cover_id: str,
                 difficulty: str, target_outcomes: List[str] = None):
        self.npc_id = npc_id
        self.player_id = player_id
        self.cover_id = cover_id
        self.difficulty = difficulty
        self.target_outcomes: List[str] = target_outcomes or []
        self.conversation_history: List[Dict] = []
        self.current_responses: List[QuickResponseOption] = []

        cfg = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["medium"])
        self.rapport: float = cfg["starting_rapport"]

    def add_message(self, text: str, is_player: bool):
        self.conversation_history.append({
            "role": "player" if is_player else "npc",
            "text": text,
        })

    @property
    def turn_count(self) -> int:
        return len([m for m in self.conversation_history if m["role"] == "player"])


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class NPCConversationService:
    """
    NPC conversation service using the Rapport mechanic.

    Quick responses carry a rapport_delta value:
      positive = builds rapport (safe, cover-appropriate conversation)
      negative = spends rapport (probing toward the objective)

    The NPC reveals information when rapport >= reveal_threshold AND the
    player's message steers toward the objective topic.
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.npc_model = settings.gemini_npc_model
        self.quick_response_model = settings.gemini_quick_response_model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.sessions: Dict[Tuple[str, str], ConversationSession] = {}
        logger.info(f"NPC Conversation Service initialized (rapport mechanic) — NPC: {self.npc_model}, QR: {self.quick_response_model}")

    def get_session(self, player_id: str, npc_id: str) -> Optional[ConversationSession]:
        return self.sessions.get((player_id, npc_id))

    # ------------------------------------------------------------------
    # Start conversation
    # ------------------------------------------------------------------

    def start_conversation(
        self,
        npc: NPCData,
        cover_id: str,
        player_id: str,
        difficulty: str,
        game_state: GameState,
        target_outcomes: List[str] = None,
    ) -> Tuple[str, List[QuickResponseOption], int]:
        """Start a new conversation. Returns (greeting, quick_responses, rapport_int)."""

        cover = next((c for c in npc.cover_options if c.cover_id == cover_id), None)
        if not cover:
            cover = npc.cover_options[0] if npc.cover_options else NPCCoverOption(
                cover_id="unknown", description="Someone at the event",
                npc_reaction="An unknown person"
            )

        session = ConversationSession(npc.id, player_id, cover_id, difficulty,
                                      target_outcomes=target_outcomes or [])
        self.sessions[(player_id, npc.id)] = session

        # Store cover in game state
        if player_id not in game_state.chosen_covers:
            game_state.chosen_covers[player_id] = {}
        game_state.chosen_covers[player_id][npc.id] = cover_id

        greeting = self._generate_greeting(npc, cover, difficulty)
        session.add_message(greeting, is_player=False)

        quick_responses = self._generate_quick_responses(npc, cover, session, difficulty)
        session.current_responses = quick_responses

        rapport_int = int(round(session.rapport))
        logger.info(f"Started conversation: {player_id} -> {npc.id} as '{cover.cover_id}' (difficulty={difficulty}, rapport={session.rapport})")
        return greeting, quick_responses, rapport_int

    # ------------------------------------------------------------------
    # Process player choice
    # ------------------------------------------------------------------

    def process_player_choice(
        self,
        response_index: int,
        player_id: str,
        npc: NPCData,
        difficulty: str,
        game_state: GameState,
    ) -> Tuple[str, List[str], int, int, List[QuickResponseOption], bool, Optional[float], List[str], bool]:
        """
        Process a quick-response choice.

        Returns: (npc_response, outcomes, rapport_int, rapport_delta_int,
                  next_quick_responses, conversation_failed, cooldown_until,
                  completed_tasks, opening_given)

        NOTE: opening_given is kept in the return signature for API compatibility
        but is always False in the rapport system.
        """
        session = self.get_session(player_id, npc.id)
        if not session:
            return ("I don't think we've met.", [], 0, 0, [], False, None, [], False)

        if response_index < 0 or response_index >= len(session.current_responses):
            response_index = 0

        chosen = session.current_responses[response_index]
        player_text = chosen.text
        rapport_delta = chosen.fit_score / 10.0  # fit_score stores rapport_delta * 10

        # Apply rapport change
        old_rapport = session.rapport
        session.rapport = max(0.0, min(5.0, session.rapport + rapport_delta))

        session.add_message(player_text, is_player=True)

        cfg = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["medium"])

        logger.info(
            f"Player chose: '{player_text[:60]}' | rapport_delta={rapport_delta:+.1f} | "
            f"rapport: {old_rapport:.1f} -> {session.rapport:.1f} | turn {session.turn_count}"
        )

        # Check for failure: rapport too low
        if session.rapport <= cfg["fail_threshold"]:
            dismissal = self._generate_failure_dismissal(npc, session, player_text, difficulty)
            session.add_message(dismissal, is_player=False)
            del self.sessions[(player_id, npc.id)]
            logger.info(f"Conversation FAILED: rapport dropped to {session.rapport:.1f}")
            rapport_int = 0
            delta_int = int(round(rapport_delta * 10))
            return (dismissal, [], rapport_int, delta_int, [], True, None, [], False)

        # Check turn limit
        if session.turn_count >= cfg["max_turns"]:
            dismissal = "It's been lovely chatting, but I really must get back to my duties. Perhaps we can talk another time."
            session.add_message(dismissal, is_player=False)
            del self.sessions[(player_id, npc.id)]
            logger.info(f"Conversation timed out after {session.turn_count} turns")
            rapport_int = int(round(session.rapport))
            delta_int = int(round(rapport_delta * 10))
            return (dismissal, [], rapport_int, delta_int, [], True, None, [], False)

        # Get NPC response with outcome detection
        cover = next((c for c in npc.cover_options if c.cover_id == session.cover_id), None)
        already_achieved = set(game_state.achieved_outcomes.get(player_id, []))
        npc_response, outcomes = self._get_npc_response(
            npc, cover, session, player_text, difficulty, already_achieved
        )

        session.add_message(npc_response, is_player=False)

        # Track achieved outcomes
        completed_tasks: List[str] = []
        if outcomes:
            if player_id not in game_state.achieved_outcomes:
                game_state.achieved_outcomes[player_id] = []
            for outcome_id in outcomes:
                if outcome_id not in game_state.achieved_outcomes[player_id]:
                    game_state.achieved_outcomes[player_id].append(outcome_id)

        # Generate next quick responses
        next_responses = self._generate_quick_responses(npc, cover, session, difficulty)
        session.current_responses = next_responses

        rapport_int = int(round(session.rapport))
        delta_int = int(round(rapport_delta * 10))

        return (npc_response, outcomes, rapport_int, delta_int, next_responses,
                False, None, completed_tasks, False)

    # ------------------------------------------------------------------
    # Greeting
    # ------------------------------------------------------------------

    def _generate_greeting(self, npc: NPCData, cover: NPCCoverOption, difficulty: str) -> str:
        story_facts = f"\n=== WORLD FACTS (never contradict these) ===\n{npc.story_context}\n" if npc.story_context else ""
        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}
{story_facts}
Someone approaches you at the event. They claim to be: {cover.description}

Your instinct about this person: {cover.npc_reaction}

{self._difficulty_prompt(difficulty)}

Generate a SHORT greeting (1-2 sentences) that reflects your reaction to this person's cover story.
Be natural and in character. Just the dialogue, no quotes or formatting."""

        try:
            return self._call_llm(prompt, self.npc_model, temperature=0.7, max_tokens=150)
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return "Oh, hello there. What can I do for you?"

    # ------------------------------------------------------------------
    # Quick response generation (rapport / steer / probe spectrum)
    # ------------------------------------------------------------------

    def _generate_quick_responses(
        self, npc: NPCData, cover: Optional[NPCCoverOption],
        session: ConversationSession, difficulty: str
    ) -> List[QuickResponseOption]:
        """Generate 3 quick responses along the rapport/steer/probe spectrum."""

        cfg = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["medium"])

        # Rapport deltas for the three options
        rapport_build = round(random.uniform(*cfg["rapport_build_range"]), 1)
        steer_delta = round(random.uniform(-0.3, 0.3), 1)
        probe_cost = -round(random.uniform(*cfg["probe_cost_range"]), 1)

        # Build target outcome descriptions for the prompt
        remaining_outcomes = self._remaining_outcomes_text(npc, session)

        recent = session.conversation_history[-6:]
        context = "\n".join(
            [f"{'Player' if m['role'] == 'player' else npc.name}: {m['text']}" for m in recent]
        )
        cover_desc = cover.description if cover else "Someone at the event"

        prompt = f"""Generate 3 response options for a player in a heist NPC conversation.

Player's cover identity: {cover_desc}
NPC: {npc.name}, {npc.role}
Conversation so far:
{context if context else "(conversation just started)"}

PLAYER'S SECRET OBJECTIVE (the player needs to extract this from the NPC):
{remaining_outcomes if remaining_outcomes else "No specific objective — just building rapport."}

Generate exactly 3 responses along this spectrum:

1. RAPPORT BUILDER (rapport_delta: {rapport_build}):
   Safe, natural conversation that fits the cover identity. Reacts to what the NPC just said,
   shows genuine interest, or demonstrates expertise fitting the cover. Does NOT mention or
   steer toward the objective. Builds trust and comfort.

2. SUBTLE STEER (rapport_delta: {steer_delta}):
   Uses the cover identity to naturally approach the objective topic WITHOUT directly asking.
   This should feel like a clever, cover-appropriate comment or question that moves the
   conversation toward the area of the objective. A skilled player picks this when they want
   to test the waters. Example: if the objective is vault codes and the cover is security
   consultant, something like "The digital access infrastructure here must be quite layered."

3. DIRECT PROBE (rapport_delta: {probe_cost}):
   Asks more directly about the objective. Gets closer to the answer but feels pushy or
   suspicious. The NPC would notice this is a pointed question. Example: "What authentication
   does the vault access system use?"

Rules:
- Keep each response SHORT: 5-15 words. Like real dialogue.
- All must fit the conversational context (respond to what the NPC just said).
- The RAPPORT BUILDER should NOT reference the objective at all.
- The SUBTLE STEER should be clever and cover-appropriate — the kind of thing only this
  cover identity would naturally say.
- The DIRECT PROBE should be noticeably more pointed but still something a person might say.
- Do NOT make any option absurd, rude, or silly.

Return ONLY a JSON array (no markdown):
[{{"text": "...", "rapport_delta": {rapport_build}}}, {{"text": "...", "rapport_delta": {steer_delta}}}, {{"text": "...", "rapport_delta": {probe_cost}}}]"""

        try:
            raw = self._call_llm(prompt, self.quick_response_model, temperature=0.8, max_tokens=400)
            raw = self._strip_code_fences(raw)
            parsed = json.loads(raw)

            responses = []
            for item in parsed[:3]:
                rd = float(item.get("rapport_delta", 0))
                responses.append(QuickResponseOption(
                    text=item["text"],
                    fit_score=int(round(rd * 10)),  # store rapport_delta * 10 in fit_score
                ))

            random.shuffle(responses)
            logger.info(f"Quick responses: {[(r.text[:40], r.fit_score/10) for r in responses]}")
            return responses

        except Exception as e:
            logger.error(f"Error generating quick responses: {e}", exc_info=True)
            return self._fallback_quick_responses(rapport_build, steer_delta, probe_cost)

    # ------------------------------------------------------------------
    # NPC response + outcome detection
    # ------------------------------------------------------------------

    def _get_npc_response(
        self, npc: NPCData, cover: Optional[NPCCoverOption],
        session: ConversationSession, player_text: str, difficulty: str,
        already_achieved: set = None,
    ) -> Tuple[str, List[str]]:
        """Get NPC response and detect outcomes. Returns (text, outcome_ids)."""

        already_achieved = already_achieved or set()
        target_outcomes = set(session.target_outcomes) if session.target_outcomes else set()
        cfg = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["medium"])

        cover_desc = cover.description if cover else "Someone at the event"
        trust_desc = cover.npc_reaction if cover else "An unknown person"

        # Separate target vs background knowledge
        target_info, target_actions, background = self._categorize_npc_knowledge(
            npc, target_outcomes, already_achieved
        )

        target_section = ""
        if target_info or target_actions:
            target_section = "=== SECRET INFORMATION (outcome IDs for the JSON) ===\n"
            if target_info:
                target_section += "Info you could share:\n" + "\n".join(target_info) + "\n"
            if target_actions:
                target_section += "Actions you could agree to:\n" + "\n".join(target_actions) + "\n"

        background_section = ""
        if background:
            background_section = "=== Other things you know (share freely as flavor) ===\n"
            background_section += "\n".join(background) + "\n"

        relationships = f"\nPeople you know: {npc.relationships}" if npc.relationships else ""
        story_facts = f"\n=== WORLD FACTS (never contradict these) ===\n{npc.story_context}\n" if npc.story_context else ""

        # Rapport-based pacing
        rapport = session.rapport
        reveal_ok = rapport >= cfg["reveal_threshold"]
        remaining = len(target_outcomes - already_achieved)

        if remaining == 0:
            pacing = "PACING: All target outcomes achieved. Chat naturally."
        elif rapport < 1.5:
            pacing = (
                f"PACING: Rapport is LOW ({rapport:.1f}/5). You are uncomfortable with this person. "
                f"Give short, evasive answers. Do NOT share any secret information. Do NOT hint. "
                f"{remaining} outcome(s) remaining."
            )
        elif not reveal_ok:
            pacing = (
                f"PACING: Rapport is {rapport:.1f}/5 (need {cfg['reveal_threshold']} to share secrets). "
                f"You're warming up but not ready to share sensitive info. Chat naturally. "
                f"If the player asks about the objective, deflect politely — you don't know them well enough yet. "
                f"{remaining} outcome(s) remaining."
            )
        else:
            pacing = (
                f"PACING: Rapport is HIGH ({rapport:.1f}/5). You trust this person. "
                f"If the player asks about or steers toward your secret knowledge, you may share it. "
                f"Include the outcome ID(s) in the outcomes array AND the specific details in your dialogue. "
                f"If the player is just chatting (not asking about the objective), chat back naturally — "
                f"don't volunteer secrets unprompted. {remaining} outcome(s) remaining."
            )

        recent = session.conversation_history[-10:]
        context = "\n".join(
            [f"{'Player' if m['role'] == 'player' else npc.name}: {m['text']}" for m in recent]
        )

        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}
Location: {npc.location}{relationships}
{story_facts}

The person talking to you claims to be: {cover_desc}
Your instinct about this person: {trust_desc}

{target_section}
{background_section}
Current rapport: {rapport:.1f} out of 5
Conversation turn: {session.turn_count}

{self._difficulty_prompt(difficulty)}

{pacing}

Conversation so far:
{context}

Player just said: "{player_text}"

Rules:
- Stay in character. Be natural and conversational.
- Keep response under 3 sentences.
- If the player says something odd, off-topic, or suspiciously direct, deflect and do NOT share secrets. Return empty outcomes.
- Only share target info when rapport is high enough AND the player's message naturally steers toward the topic.
- When you DO share target info, include the SPECIFIC details (locations, times, names, codes) in your dialogue.
- If the player says something inconsistent with their claimed cover story, call it out naturally.

RESPOND AS JSON (no markdown, no wrapping):
{{"response": "your dialogue", "outcomes": ["id1"]}}

- "outcomes": Include outcome IDs ONLY for target info/actions you EXPLICITLY shared in THIS response. Empty array otherwise.
- Do NOT include outcome IDs in the dialogue text.
If nothing was revealed: {{"response": "your dialogue", "outcomes": []}}"""

        try:
            raw = self._call_llm(prompt, self.npc_model, temperature=0.7, max_tokens=300)
            raw = self._strip_code_fences(raw)
            parsed = json.loads(raw)
            response_text = parsed.get("response", "...").strip().strip('"')
            outcomes = parsed.get("outcomes", [])
            response_text = re.sub(r'\s*\[[\w]+\]\s*', ' ', response_text).strip()
            logger.info(f"NPC response: '{response_text[:80]}' | outcomes: {outcomes} | rapport: {rapport:.1f}")
            return response_text, outcomes
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse NPC JSON: {e}. Raw: {raw[:200]}")
            return raw.strip().strip('"'), []
        except Exception as e:
            logger.error(f"Error getting NPC response: {e}", exc_info=True)
            return "Hmm, let me think about that.", []

    # ------------------------------------------------------------------
    # Failure dismissal
    # ------------------------------------------------------------------

    def _generate_failure_dismissal(
        self, npc: NPCData, session: ConversationSession,
        last_player_text: str, difficulty: str
    ) -> str:
        story_facts = f"\n=== WORLD FACTS ===\n{npc.story_context}\n" if npc.story_context else ""
        prompt = f"""You are {npc.name}, a {npc.role}.
Personality: {npc.personality}
{story_facts}
You've been talking to someone who has made you uncomfortable. You don't trust them.
The last thing they said was: "{last_player_text}"

End this conversation naturally and firmly. 1-2 sentences. Just the dialogue."""

        try:
            return self._call_llm(prompt, self.npc_model, temperature=0.7, max_tokens=150)
        except Exception as e:
            logger.error(f"Error generating dismissal: {e}")
            return "I don't think I should be talking to you anymore. Please excuse me."

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _remaining_outcomes_text(self, npc: NPCData, session: ConversationSession) -> str:
        """Build a description of what the player still needs to extract."""
        target_ids = set(session.target_outcomes)
        if not target_ids:
            return ""

        lines = []
        for item in npc.information_known:
            if item.info_id and item.info_id in target_ids:
                lines.append(f"- [{item.info_id}] {item.description}")
        for action in npc.actions_available:
            if action.action_id in target_ids:
                lines.append(f"- [{action.action_id}] {action.description}")
        return "\n".join(lines) if lines else ""

    def _categorize_npc_knowledge(
        self, npc: NPCData, target_outcomes: set, already_achieved: set
    ) -> Tuple[List[str], List[str], List[str]]:
        """Split NPC knowledge into target info, target actions, and background."""
        target_info, target_actions, background = [], [], []
        for item in npc.information_known:
            if item.info_id:
                if item.info_id in already_achieved:
                    continue
                elif item.info_id in target_outcomes:
                    target_info.append(f"- [{item.info_id}] {item.description}")
                else:
                    background.append(f"- {item.description} (flavor)")
            else:
                background.append(f"- {item.description} (flavor)")

        for action in npc.actions_available:
            if action.action_id in already_achieved:
                continue
            elif action.action_id in target_outcomes:
                target_actions.append(f"- [{action.action_id}] {action.description}")
            else:
                background.append(f"- {action.description} (flavor)")

        return target_info, target_actions, background

    def _difficulty_prompt(self, difficulty: str) -> str:
        if difficulty == "easy":
            return """Difficulty: easy
- Accept their cover story at face value. Be friendly.
- When rapport is high and they ask about your secrets, share willingly."""
        elif difficulty == "hard":
            return """Difficulty: hard
- Be observant and skeptical. Notice inconsistencies.
- Even at high rapport, require the question to feel very natural before sharing secrets."""
        else:
            return """Difficulty: medium
- Be realistic — friendly but not giving away secrets to strangers.
- At high rapport, share if the question feels natural for the conversation."""

    def _fallback_quick_responses(
        self, rapport_build: float, steer_delta: float, probe_cost: float
    ) -> List[QuickResponseOption]:
        responses = [
            QuickResponseOption(text="So what's your role here tonight?", fit_score=int(round(rapport_build * 10))),
            QuickResponseOption(text="Anything interesting happen tonight?", fit_score=int(round(steer_delta * 10))),
            QuickResponseOption(text="I heard there's some valuable items here.", fit_score=int(round(probe_cost * 10))),
        ]
        random.shuffle(responses)
        return responses

    def _strip_code_fences(self, raw: str) -> str:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        return raw

    def _call_llm(self, prompt: str, model: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
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


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

_npc_service: Optional[NPCConversationService] = None


def get_npc_conversation_service() -> NPCConversationService:
    global _npc_service
    if _npc_service is None:
        _npc_service = NPCConversationService()
    return _npc_service
