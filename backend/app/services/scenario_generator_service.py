"""
Scenario Generator Service

Thin async wrapper around the shared scenario_pipeline.run_pipeline().
Called from handle_start_game when the requested scenario file doesn't exist.
Players see progress via WebSocket broadcasts while the scenario is built.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Callable, Awaitable, List

logger = logging.getLogger(__name__)

_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"


async def generate_scenario(
    scenario_id: str,
    roles: List[str],
    broadcast: Callable[[str], Awaitable[None]],
) -> bool:
    """
    Generate a scenario on the fly and broadcast progress to the room.

    Args:
        scenario_id: e.g. "museum_gala_vault"
        roles: list of role_ids selected by players
        broadcast: async callable that sends a progress string to all room players

    Returns:
        True if generation succeeded and the file is ready to load.
    """
    await broadcast(f"🎲 Generating scenario '{scenario_id}' for {len(roles)} players...")

    # Ensure scripts/ is importable inside the thread
    scripts_str = str(_SCRIPTS_DIR)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)

    def _run_pipeline():
        from scenario_pipeline import run_pipeline
        return run_pipeline(
            scenario_id=scenario_id,
            roles=roles,
            progress_fn=lambda msg: logger.info(f"[generator] {msg}"),
        )

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, _run_pipeline)
    except Exception as e:
        logger.error(f"[generator] Unexpected error: {e}", exc_info=True)
        await broadcast(f"❌ Scenario generation failed: {e}")
        return False

    if result.success:
        await broadcast(
            f"✅ Scenario ready — "
            f"{result.tasks} tasks, {result.locations} locations, {result.items} items"
        )
        return True
    else:
        await broadcast(f"❌ Scenario generation failed: {result.error}")
        return False
