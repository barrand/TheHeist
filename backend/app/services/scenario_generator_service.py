"""
Scenario Generator Service

Generates a scenario on-demand when a requested experience file doesn't exist.
Runs the same pipeline as the E2E portal: procedural_generator → graph_validator_fixer
→ json_exporter → markdown_renderer → validate_scenario → scenario_editor_agent.

Designed to be called from handle_start_game so players see progress via WebSocket
broadcasts while the scenario is being built.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Callable, Awaitable, List

logger = logging.getLogger(__name__)

# Path to backend/scripts/ — where generators and validators live
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
_EXPERIENCES_DIR = Path(__file__).parent.parent.parent / "experiences"


async def generate_scenario(
    scenario_id: str,
    roles: List[str],
    broadcast: Callable[[str], Awaitable[None]],
) -> bool:
    """
    Generate a scenario on the fly.

    Args:
        scenario_id: e.g. "museum_gala_vault"
        roles: list of role names selected by players
        broadcast: async callable that sends a progress string to all players in the room

    Returns:
        True if generation succeeded and the file is ready to load, False otherwise.
    """
    await broadcast(f"🎲 Scenario not found — generating '{scenario_id}' for {len(roles)} players...")

    # All generation code is synchronous (CPU + LLM calls), so run it in a thread
    # to avoid blocking the asyncio event loop.
    loop = asyncio.get_event_loop()

    def _run_pipeline():
        """Synchronous generation pipeline — runs in a thread pool."""
        if str(_SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(_SCRIPTS_DIR))

        from generators.procedural_generator import generate_scenario_graph, GeneratorConfig
        from generators.graph_validator_fixer import validate_and_fix_graph
        from generators.json_exporter import export_to_json
        from generators.markdown_renderer import export_to_markdown
        from validate_scenario import ScenarioValidator, ValidationLevel

        logger.info(f"[generator] Building graph: {scenario_id} {roles}")
        config = GeneratorConfig()
        graph = generate_scenario_graph(scenario_id, roles, config)
        logger.info(f"[generator] Graph: {len(graph.tasks)} tasks, {len(graph.locations)} locations")

        logger.info("[generator] Validating and fixing graph...")
        fixed_graph, validation_result = validate_and_fix_graph(graph, max_iterations=10)
        if not validation_result.is_valid:
            raise RuntimeError(f"Graph validation failed: {validation_result.errors}")
        fixes = len(validation_result.fixes_applied)
        logger.info(f"[generator] Graph valid" + (f" ({fixes} auto-fixed)" if fixes else ""))

        logger.info("[generator] Exporting to JSON and markdown...")
        export_to_json(fixed_graph)
        export_to_markdown(fixed_graph)
        player_count = len(roles)
        md_filename = f"generated_{scenario_id}_{player_count}players.md"
        md_path = _EXPERIENCES_DIR / md_filename
        logger.info(f"[generator] Exported: {md_filename}")

        logger.info("[generator] Validating markdown...")
        validator = ScenarioValidator(md_path)
        report = validator.validate_all()
        critical = [i for i in report.issues if i.level == ValidationLevel.CRITICAL]
        logger.info(f"[generator] Validation: {len(critical)} critical issues")

        if critical:
            logger.info(f"[generator] Running editor to fix {len(critical)} critical issues...")
            from scenario_editor_agent import ScenarioEditorAgent
            agent = ScenarioEditorAgent()
            results = agent.fix_issues(md_path, critical)
            fixed = sum(1 for r in results if r.success)
            logger.info(f"[generator] Editor: {fixed}/{len(critical)} fixed")

        logger.info("[generator] Generation complete ✅")
        return md_filename

    try:
        await broadcast("⚙️  Building scenario graph...")
        filename = await loop.run_in_executor(None, _run_pipeline)
        await broadcast(f"✅ Scenario ready — starting game...")
        return True

    except Exception as e:
        logger.error(f"[generator] Generation failed: {e}", exc_info=True)
        await broadcast(f"❌ Scenario generation failed: {e}")
        return False
