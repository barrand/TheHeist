"""
Scenario Generator Service

Thin async wrapper around the shared scenario_pipeline.run_pipeline().
Called from handle_start_game when the requested scenario file doesn't exist.
Players see progress via WebSocket broadcasts while the scenario is built.
"""

import asyncio
import logging
import queue
import sys
from pathlib import Path
from typing import Callable, Awaitable, List

logger = logging.getLogger(__name__)

_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"

# Spoiler-free progress messages keyed by pipeline phase.
# The pipeline emits technical messages; we map them to player-friendly ones.
_PHASE_MESSAGES = {
    "Loading generators...": ("📋 Assembling the crew dossier...", "phase_load"),
    "Generating scenario graph...": ("🗺️ Scouting the target...", "phase_graph"),
    "── [1/3] Graph topology fix...": ("🔗 Planning the approach...", "phase_topology"),
    "Exporting to JSON and markdown...": ("📝 Writing the briefing...", "phase_export"),
    "── [2/3] Playability simulation...": ("🎯 Running rehearsals...", "phase_simulate"),
    "── [3/3] NPC quality check...": ("🎭 Casting the characters...", "phase_npc"),
}


def _to_player_message(raw_msg: str) -> tuple[str | None, str | None]:
    """Convert a raw pipeline message to a spoiler-free player message.

    Returns (player_message, phase_id) or (None, None) if the message
    should be suppressed (e.g. internal debug detail).
    """
    stripped = raw_msg.strip()

    if stripped in _PHASE_MESSAGES:
        return _PHASE_MESSAGES[stripped]

    if "Graph complete:" in stripped:
        return ("🏗️ Blueprint ready — laying out the locations...", "phase_graph_done")

    if "Topology fixed" in stripped or "Topology clean" in stripped:
        return ("✅ Approach looks solid", "phase_topology_done")

    if "Playability OK" in stripped:
        return ("✅ Rehearsal passed — no dead ends", "phase_simulate_done")

    if "Deadlock detected" in stripped:
        return ("⚠️ Adjusting the plan...", "phase_simulate_retry")

    if stripped.startswith("♻️") and "regenerating" in stripped:
        return ("🔄 Reworking the plan...", "phase_retry")

    if "No NPC quality issues" in stripped or "All NPC quality issues resolved" in stripped:
        return ("✅ Characters are ready", "phase_npc_done")

    if "NPC quality issue" in stripped and "sending to editor" in stripped:
        return ("✏️ Polishing the characters...", "phase_npc_edit")

    if stripped.startswith("✅ Done") or stripped.startswith("⚠️  Done"):
        return ("🎬 Scenario locked — preparing the job...", "phase_done")

    if stripped.startswith("❌"):
        clean = stripped.lstrip("❌ ").strip()
        return (f"❌ {clean}", "phase_error")

    return (None, None)


async def generate_scenario(
    scenario_id: str,
    roles: List[str],
    broadcast: Callable[[str], Awaitable[None]],
) -> bool:
    """
    Generate a scenario on the fly and broadcast progress to the room.
    """
    await broadcast("🎲 Planning the heist...")

    scripts_str = str(_SCRIPTS_DIR)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)

    progress_queue: queue.Queue[str] = queue.Queue()

    def _run_pipeline():
        from scenario_pipeline import run_pipeline
        return run_pipeline(
            scenario_id=scenario_id,
            roles=roles,
            progress_fn=lambda msg: progress_queue.put(msg),
        )

    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, _run_pipeline)

    # Drain the queue while the pipeline runs, broadcasting player-friendly messages
    last_phase = None
    while not future.done():
        await asyncio.sleep(0.3)
        while not progress_queue.empty():
            try:
                raw = progress_queue.get_nowait()
            except queue.Empty:
                break
            player_msg, phase = _to_player_message(raw)
            if player_msg and phase != last_phase:
                last_phase = phase
                await broadcast(player_msg)

    # Drain any remaining messages after pipeline completes
    while not progress_queue.empty():
        try:
            raw = progress_queue.get_nowait()
        except queue.Empty:
            break
        player_msg, phase = _to_player_message(raw)
        if player_msg and phase != last_phase:
            last_phase = phase
            await broadcast(player_msg)

    try:
        result = future.result()
    except Exception as e:
        logger.error(f"[generator] Unexpected error: {e}", exc_info=True)
        await broadcast(f"❌ Scenario generation failed: {e}")
        return False

    if result.success:
        from app.services.storage_service import storage
        storage.sync_local_to_gcs("experiences")

        await broadcast(
            f"✅ Scenario ready — "
            f"{result.tasks} tasks, {result.locations} locations, {result.items} items"
        )
        return True
    else:
        await broadcast(f"❌ Scenario generation failed: {result.error}")
        return False
