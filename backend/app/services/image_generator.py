"""
Image generation service with manifest-based staleness detection.

Each experience's images are stored under generated_images/{experience_id}/.
A _manifest.json file tracks which images belong to the current scenario
version via a content hash of the experience data. When the scenario is
regenerated (new locations, items, NPCs), the hash changes and stale
images are cleaned up before new ones are generated.
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

_generation_tasks: dict[str, bool] = {}
_MANIFEST_FILENAME = "_manifest.json"


# ------------------------------------------------------------------
# Manifest helpers
# ------------------------------------------------------------------

def _content_hash(experience_dict: Dict) -> str:
    """Deterministic MD5 hash of the experience data that drives image generation.
    
    Only hashes fields that affect image content (locations, items, NPCs) —
    metadata like scenario_id/objective are excluded so adding context fields
    doesn't invalidate existing manifests.
    """
    image_data = {
        k: experience_dict[k]
        for k in ("locations", "items_by_location", "npcs")
        if k in experience_dict
    }
    serialized = json.dumps(image_data, sort_keys=True, default=str)
    return hashlib.md5(serialized.encode()).hexdigest()


def _expected_filenames(locations: List[Dict], items: List[Dict], npcs: List[Dict]) -> list[str]:
    """Build the exact set of image filenames expected for this experience."""
    names: list[str] = []
    for loc in locations:
        names.append(f"location_{loc['id']}.png")
    for item in items:
        clean_id = item['id'].removeprefix("item_")
        names.append(f"item_{clean_id}.png")
    for npc in npcs:
        names.append(f"npc_{npc['id']}.png")
    return sorted(names)


@dataclass
class ImageCheckResult:
    ready: bool
    missing: list[str] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)
    present: list[str] = field(default_factory=list)


def _read_manifest(experience_id: str) -> Optional[dict]:
    """Read manifest from local disk or GCS via StorageService."""
    from app.services.storage_service import storage
    key = f"generated_images/{experience_id}/{_MANIFEST_FILENAME}"
    text = storage.read_text(key)
    if text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning(f"Corrupt manifest for {experience_id}, treating as missing")
    return None


def _write_manifest(experience_id: str, cache_name: str, content_hash: str, image_files: list[str]):
    """Write manifest to local disk + GCS."""
    from app.services.storage_service import storage
    manifest = {
        "cache_name": cache_name,
        "content_hash": content_hash,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "images": sorted(image_files),
    }
    key = f"generated_images/{experience_id}/{_MANIFEST_FILENAME}"
    storage.write_text(key, json.dumps(manifest, indent=2))
    logger.info(f"📋 Manifest written: {len(image_files)} images, hash={content_hash[:8]}")


# ------------------------------------------------------------------
# Experience parsing
# ------------------------------------------------------------------

def parse_experience_for_generation(experience_dict: Dict) -> tuple[List[Dict], List[Dict], List[Dict]]:
    """Parse experience data to extract locations, items, and NPCs that need images."""
    locations = []
    items = []
    npcs = []

    if 'locations' in experience_dict:
        for loc in experience_dict['locations']:
            if isinstance(loc, dict):
                locations.append({
                    'name': loc.get('name', ''),
                    'id': loc.get('id', ''),
                    'visual': loc.get('visual', '')
                })
            else:
                location_id = loc.lower().replace(' ', '_').replace('-', '_')
                locations.append({'name': loc, 'id': location_id, 'visual': ''})

    if 'items_by_location' in experience_dict:
        seen_items: set[str] = set()
        for location_items in experience_dict['items_by_location'].values():
            for item in location_items:
                item_id = item.get('id', '')
                if item_id and item_id not in seen_items:
                    seen_items.add(item_id)
                    items.append({
                        'id': item_id,
                        'name': item.get('name', ''),
                        'description': item.get('description', ''),
                        'visual': item.get('visual', '')
                    })

    if 'npcs' in experience_dict:
        for npc in experience_dict['npcs']:
            npcs.append({
                'id': npc.get('id', ''),
                'name': npc.get('name', ''),
                'role': npc.get('role', ''),
                'location': npc.get('location', ''),
                'gender': npc.get('gender', 'person'),
                'ethnicity': npc.get('ethnicity', ''),
                'clothing': npc.get('clothing', ''),
                'expression': npc.get('expression', 'friendly'),
                'attitude': npc.get('attitude', 'approachable'),
                'details': npc.get('details', ''),
            })

    return locations, items, npcs


# ------------------------------------------------------------------
# Manifest-based image check
# ------------------------------------------------------------------

def check_images_exist(
    experience_id: str,
    experience_dict: Dict,
    cache_name: str = "",
) -> ImageCheckResult:
    """
    Check if the correct images exist for this experience version.

    Compares a content hash of experience_dict against the stored manifest.
    If the hash matches, checks each expected file individually.
    If the hash differs (or no manifest), all existing images are stale.
    """
    from app.services.storage_service import storage

    locations, items, npcs = parse_experience_for_generation(experience_dict)
    expected = _expected_filenames(locations, items, npcs)
    current_hash = _content_hash(experience_dict)
    prefix = f"generated_images/{experience_id}"

    manifest = _read_manifest(experience_id)

    if manifest and manifest.get("content_hash") == current_hash:
        logger.info(
            f"📋 Manifest match for {experience_id} "
            f"(hash={current_hash[:8]}, cache={manifest.get('cache_name', '?')})"
        )
        # Hash matches — check each expected file exists (locally or GCS)
        present = []
        missing = []
        for fname in expected:
            key = f"{prefix}/{fname}"
            if storage.exists(key):
                present.append(fname)
            else:
                missing.append(fname)

        if not missing:
            logger.info(f"✅ All {len(expected)} images present for {experience_id}")
            return ImageCheckResult(ready=True, present=present)

        logger.info(
            f"⚠️ Manifest valid but {len(missing)} images missing locally: "
            f"{missing[:5]}{'...' if len(missing) > 5 else ''}"
        )
        return ImageCheckResult(ready=False, missing=missing, present=present)

    # Hash mismatch or no manifest — all on-disk images are stale
    if manifest:
        logger.info(
            f"🔄 Manifest hash mismatch for {experience_id}: "
            f"manifest={manifest.get('content_hash', '?')[:8]}, "
            f"current={current_hash[:8]} — all images stale"
        )
    else:
        logger.info(f"📋 No manifest for {experience_id} — treating all images as stale")

    # Find stale files on local disk
    images_dir = Path(__file__).parent.parent.parent / "generated_images" / experience_id
    stale = []
    if images_dir.is_dir():
        for f in images_dir.iterdir():
            if f.is_file() and f.suffix == ".png":
                stale.append(f.name)

    return ImageCheckResult(
        ready=False,
        missing=expected,
        stale=stale,
        present=[],
    )


# ------------------------------------------------------------------
# Main generation entry point
# ------------------------------------------------------------------

async def generate_all_images_for_experience(
    experience_id: str,
    experience_dict: Dict,
    cache_name: str = "",
    broadcast: Optional[Callable[[str], Awaitable[None]]] = None,
) -> bool:
    """
    Generate all images for an experience at game start.
    Uses manifest-based staleness detection to avoid regenerating
    images that already match the current scenario version.
    """
    # Wait if another generation is in progress for this experience
    if experience_id in _generation_tasks:
        logger.info(f"🎨 Images already generating for {experience_id}, waiting...")
        while experience_id in _generation_tasks:
            await asyncio.sleep(0.5)
        return True

    check = check_images_exist(experience_id, experience_dict, cache_name)
    if check.ready:
        logger.info(f"✅ All images up-to-date for {experience_id}")
        return True

    if broadcast:
        total = len(check.missing)
        await broadcast(f"🖼️ Generating {total} images...")

    # Clean stale images from local disk
    if check.stale:
        from app.services.storage_service import storage
        logger.info(f"🗑️ Removing {len(check.stale)} stale images for {experience_id}")
        for fname in check.stale:
            storage.delete_local(f"generated_images/{experience_id}/{fname}")

    locations, items, npcs = parse_experience_for_generation(experience_dict)

    # Build scenario context string for image prompts
    scenario_id = experience_dict.get("scenario_id", "")
    objective = experience_dict.get("objective", "")
    scenario_context = scenario_id.replace("_", " ") if scenario_id else ""
    if objective:
        scenario_context = f"{scenario_context} — {objective}" if scenario_context else objective

    logger.info(
        f"🎨 Generating images for {experience_id}: "
        f"{len(locations)} locations, {len(items)} items, {len(npcs)} NPCs"
    )
    if scenario_context:
        logger.info(f"🎨 Scenario context: {scenario_context}")

    try:
        import sys
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        from generate_location_images import generate_all_location_images
        from generate_item_images import generate_all_item_images
        from generate_npc_images import generate_all_npc_images

        _generation_tasks[experience_id] = True

        phase_completed = [0]
        phase_total = [0]
        current_phase = [""]

        async def _on_image_done():
            phase_completed[0] += 1
            if broadcast:
                await broadcast(f"🎨 {current_phase[0]} ({phase_completed[0]}/{phase_total[0]})")

        logger.info(f"🎨 Step 1/3: Generating location images...")
        current_phase[0] = "Rendering locations"
        phase_completed[0] = 0
        phase_total[0] = len(locations)
        if broadcast:
            await broadcast(f"🖼️ Rendering {len(locations)} locations...")
        await generate_all_location_images(
            experience_id, locations,
            on_progress=_on_image_done,
            scenario_context=scenario_context,
        )

        logger.info(f"🎨 Step 2/3: Generating item images...")
        current_phase[0] = "Drawing items"
        phase_completed[0] = 0
        phase_total[0] = len(items)
        if broadcast:
            await broadcast(f"🔧 Drawing {len(items)} items...")
        await generate_all_item_images(experience_id, items, on_progress=_on_image_done)

        logger.info(f"🎨 Step 3/3: Generating NPC images...")
        current_phase[0] = "Sketching characters"
        phase_completed[0] = 0
        phase_total[0] = len(npcs)
        if broadcast:
            await broadcast(f"🎭 Sketching {len(npcs)} characters...")
        await generate_all_npc_images(experience_id, npcs, on_progress=_on_image_done)

        # Write manifest and sync to GCS
        from app.services.storage_service import storage
        expected = _expected_filenames(locations, items, npcs)
        _write_manifest(experience_id, cache_name, _content_hash(experience_dict), expected)
        storage.sync_local_to_gcs(f"generated_images/{experience_id}")

        logger.info(f"✅ All images generated for {experience_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Image generation failed for {experience_id}: {e}")
        return False
    finally:
        _generation_tasks.pop(experience_id, None)
