#!/usr/bin/env python3
"""
Pre-generate quick-start scenarios defined in shared_data/quick_scenarios.json.

Usage:
    cd backend && python scripts/generate_quick_scenarios.py

Each entry that already has a cached .md and .json file is skipped.
Set FORCE=1 to regenerate everything.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Ensure project root is on the path so local imports work
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "scripts"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _load_config() -> list[dict]:
    config_path = BACKEND_DIR.parent / "shared_data" / "quick_scenarios.json"
    with open(config_path) as f:
        return json.load(f).get("scenarios", [])


def _scenario_exists(scenario_id: str, roles: list[str]) -> bool:
    from app.services.experience_loader import scenario_cache_filename

    base = scenario_cache_filename(scenario_id, sorted(roles))
    exp_dir = BACKEND_DIR / "experiences"
    return (exp_dir / f"{base}.md").exists() or (exp_dir / f"{base}.json").exists()


def _generate_scenario(entry: dict) -> bool:
    from scenario_pipeline import run_pipeline

    scenario_id = entry["scenario_id"]
    roles = sorted(entry["roles"])

    logger.info(f"--- Generating: {scenario_id} with {roles} ---")
    result = run_pipeline(
        scenario_id,
        roles,
        progress_fn=lambda msg: logger.info(f"  {msg}"),
    )
    if result.success:
        logger.info(f"  OK  md_path={result.md_path}")
    else:
        logger.error(f"  FAILED  error={result.error}")
    return result.success


async def _generate_images(entry: dict) -> bool:
    from app.services.experience_loader import ExperienceLoader, scenario_cache_filename
    from app.services.image_generator import generate_all_images_for_experience

    scenario_id = entry["scenario_id"]
    roles = sorted(entry["roles"])
    cache_base = scenario_cache_filename(scenario_id, roles)

    loader = ExperienceLoader(experiences_dir="experiences")
    game_state = loader.load_experience(scenario_id, roles)

    experience_dict = {
        "locations": [loc.model_dump() for loc in game_state.locations],
        "items_by_location": {
            loc: [item.model_dump() for item in items]
            for loc, items in game_state.items_by_location.items()
        },
        "npcs": [npc.model_dump() for npc in game_state.npcs],
    }

    logger.info(f"  Generating images for {cache_base}...")
    ok = await generate_all_images_for_experience(
        cache_base,
        experience_dict,
        cache_name=cache_base,
        broadcast=lambda msg: logger.info(f"    {msg}"),
    )
    return ok


def main():
    force = os.getenv("FORCE", "").lower() in ("1", "true", "yes")
    entries = _load_config()
    logger.info(f"Found {len(entries)} quick scenario(s) to pre-generate")

    for entry in entries:
        sid = entry["scenario_id"]
        roles = sorted(entry["roles"])
        exists = _scenario_exists(sid, roles)

        if exists and not force:
            logger.info(f"SKIP (already exists): {sid} / {roles}")
            continue

        ok = _generate_scenario(entry)
        if not ok:
            logger.error(f"Scenario generation failed for {sid} — skipping images")
            continue

        asyncio.run(_generate_images(entry))

    logger.info("Done.")


if __name__ == "__main__":
    main()
